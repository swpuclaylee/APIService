import os
import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY


# 用户认证类
class Auth:
    hasher = CryptContext(schemes=['bcrypt'])
    secret_key = SECRET_KEY  # 后面改成从环境变量中获取

    # 用户密码加密
    def encode_password(self, password: str) -> str:
        hashed_password = self.hasher.hash(password)
        return hashed_password

    # 用户密码验证
    def verify_password(self, hashed_password: str, password: str) -> bool:
        return self.hasher.verify(password, hashed_password)

    # 生成访问token
    def encode_token(self, user_id: int, user_name: str, user_phone: str, user_admin: int) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, hours=2),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': {
                'user_id': user_id,
                'user_name': user_name,
                'user_phone': user_phone,
                'user_admin': user_admin
            }
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )

    # 解析访问token
    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload['scope'] == 'access_token':
                return payload['sub']
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    # 生成刷新token
    def encode_refresh_token(self, user_id: int, user_name: str, user_phone: str, user_admin: int) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, hours=24),
            'iat': datetime.utcnow(),
            'scope': 'refresh_token',
            'sub': {
                'user_id': user_id,
                'user_name': user_name,
                'user_phone': user_phone,
                'user_admin': user_admin
            }
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )

    # 刷新token
    def refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=['HS256'])
            if payload['scope'] == 'refresh_token':
                user_id = payload['sub'].get('user_id')
                user_name = payload['sub'].get('user_name')
                user_phone = payload['sub'].get('user_phone')
                user_admin = payload['sub'].get('user_admin')
                new_token = self.encode_token(user_id, user_name, user_phone, user_admin)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')
