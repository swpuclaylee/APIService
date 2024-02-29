import logging

from fastapi import APIRouter, Request, Query, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.untils.reponse_untils import my_response
from app.untils.authentication_untils import send_sms_to_number
from app.core.database import get_db
from app.core.config import SMS_DAILY_LIMIT, log_name
from app.enums.response_enums import ResponseEnum
from app.models.blog_models import User
from app.core.auth import Auth

router = APIRouter()
auth_handler = Auth()

logger = logging.getLogger(log_name)


# 短信发送验证码
@router.post('/sms/send')
async def send_sms(request: Request, mobile: str = Query(..., title='Mobile Number')):
    sms_mobile_count = await request.app.state.redis.get(f'sms:limit:{mobile}')
    if sms_mobile_count and int(sms_mobile_count) >= SMS_DAILY_LIMIT:
        return my_response(result=ResponseEnum.SMS_EXCEEDING_LIMIT.value.get('code'),
                           msg=ResponseEnum.SMS_EXCEEDING_LIMIT.value.get('message'),
                           content='')
    client_ip = request.client.host
    sms_ip_count = await request.app.state.redis.get(f'sms:limit:{client_ip}')
    if sms_ip_count and int(sms_ip_count) >= SMS_DAILY_LIMIT:
        return my_response(result=ResponseEnum.SMS_EXCEEDING_LIMIT.value.get('code'),
                           msg=ResponseEnum.SMS_EXCEEDING_LIMIT.value.get('message'),
                           content='')
    response = await send_sms_to_number(request, mobile)
    return response


# 账号密码登录
@router.post('/account/login')
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first() or db.query(User).filter(
        User.mobile == username).first()
    if not user:
        return my_response(result=ResponseEnum.USER_NOT_EXIST.value.get('code'),
                           msg=ResponseEnum.USER_NOT_EXIST.value.get('message'), content='')
    if not auth_handler.verify_password(user.password, password):
        return my_response(result=ResponseEnum.USERNAME_OR_PASSWORD_ERROR.value.get('code'),
                           msg=ResponseEnum.USERNAME_OR_PASSWORD_ERROR.value.get('message'), content='')
    user_id, user_name, user_phone, user_admin = user.id, user.username, user.mobile, user.admin
    access_token = auth_handler.encode_token(user_id, user_name, user_phone, user_admin)
    refresh_token = auth_handler.encode_refresh_token(user_id, user_name, user_phone, user_admin)
    content = {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token
    }
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'),
                       msg=ResponseEnum.SUCCESS.value.get('message'),
                       content=content)


# 手机号验证码登录
@router.post('/mobile/login')
async def mobile_login(request: Request, mobile: str, code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == mobile).first()
    if not user:
        return my_response(result=ResponseEnum.USER_NOT_EXIST.value.get('code'),
                           msg=ResponseEnum.USER_NOT_EXIST.value.get('message'), content='')
    if not await request.app.state.redis.get(mobile):
        return my_response(result=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('message'),
                           content='')
    if not code == await request.app.state.redis.get(mobile):
        return my_response(result=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('message'),
                           content='')
    user_id, user_name, user_phone, user_admin = user.id, user.username, user.mobile, user.admin
    access_token = auth_handler.encode_token(user_id, user_name, user_phone, user_admin)
    refresh_token = auth_handler.encode_refresh_token(user_id, user_name, user_phone, user_admin)
    content = {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token
    }
    await request.app.state.redis.delete(mobile)
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'),
                       msg=ResponseEnum.SUCCESS.value.get('message'),
                       content=content)


