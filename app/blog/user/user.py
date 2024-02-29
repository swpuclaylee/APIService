import logging

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.untils.reponse_untils import my_response
from app.enums.response_enums import ResponseEnum
from app.core.database import get_db
from app.models.blog_models import User
from app.core.config import log_name
from app.core.auth import Auth
from app.untils.authentication_untils import generate_verification_code

router = APIRouter()

logger = logging.getLogger(log_name)
auth_handler = Auth()


# 用户注册
@router.post('/register')
async def register(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')
    mobile = data.get('mobile')
    verification_code = data.get('code')
    user = db.query(User).filter(User.username == username).first()
    if user:
        return my_response(result=ResponseEnum.USER_NAME_ALREADY_EXISTS.value.get('code'),
                           msg=ResponseEnum.USER_NAME_ALREADY_EXISTS.value.get('message'), content='')
    user = db.query(User).filter(User.mobile == mobile).first()
    if user:
        return my_response(result=ResponseEnum.USER_ALREADY_EXISTS.value.get('code'),
                           msg=ResponseEnum.USER_ALREADY_EXISTS.value.get('message'), content='')
    cache_verification_code = await request.app.state.redis.get(mobile)
    if cache_verification_code is None:
        return my_response(result=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('message'), content='')
    if cache_verification_code != verification_code:
        return my_response(result=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('message'), content='')
    hashed_password = auth_handler.encode_password(password)
    try:
        user = User(username=username, password=hashed_password, mobile=mobile)
        db.add(user)
        db.commit()
    except Exception as e:
        logger.error(f'{mobile} 注册用户失败，{e}')
        db.rollback()
        return my_response(result=ResponseEnum.REGISTRATION_FAILED.value.get('code'),
                           msg=ResponseEnum.REGISTRATION_FAILED.value.get('message'), content='')
    await request.app.state.redis.delete(mobile)
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'), msg=ResponseEnum.SUCCESS.value.get('message'),
                       content='')


# 获取用户信息
@router.get('/info')
async def user_info(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    _, hashed_token = auth_header.split(' ')
    if not auth_header or not hashed_token:
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    try:
        sub = auth_handler.decode_token(hashed_token)
    except Exception as e:
        logger.error(f'Error decoding token: {e}')
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    user_id = sub.get('user_id')
    user = db.query(User).filter(User.id == user_id).first()
    if user.admin == 1:
        roles = ['admin']
    else:
        roles = ['user']
    content = {
        "id": user.id,
        "username": user.username,
        "mobile": user.mobile,
        "nickname": user.nickname,
        "gender": user.gender,
        "birthday": datetime.strftime(user.birthday, '%Y-%m-%d %H:%M:%S') if user.birthday else user.birthday,
        "email": user.email,
        "brief": user.brief,
        "avatar": user.avatar,
        "status": user.status,
        "admin": user.admin,
        "roles": roles
    }
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'),
                       msg=ResponseEnum.SUCCESS.value.get('message'),
                       content=content)


# 更新用户信息
@router.post('/update')
async def update(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    _, hashed_token = auth_header.split(' ')
    if not auth_header or not hashed_token:
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    try:
        sub = auth_handler.decode_token(hashed_token)
    except Exception as e:
        logger.error(f'Error decoding token: {e}')
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    data = await request.json()
    user_id = data.get('userId')
    birthday = data.get('birthday')
    brief = data.get('brief')
    gender = data.get('gender')
    nickname = data.get('nickname')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return my_response(result=ResponseEnum.USER_NOT_EXIST.value.get('code'),
                           msg=ResponseEnum.USER_NOT_EXIST.value.get('message'), content='')
    try:
        if birthday is not None:
            if birthday == '':
                birthday = None
            else:
                birthday = datetime.strptime(birthday, '%Y-%m-%dT%H:%M:%S.%fZ')
                birthday = birthday.strftime('%Y-%m-%d %H:%M:%S')
            user.birthday = birthday
        if brief is not None:
            if brief == '':
                brief = None
            user.brief = brief
        if gender is not None:
            if gender == '':
                gender = None
            user.gender = gender
        if nickname is not None:
            if nickname == '':
                nickname = None
            user.nickname = nickname
        db.commit()
    except Exception as e:
        logger.error(f'{user.username} 更新用户信息失败，{e}')
        db.rollback()
        return my_response(result=ResponseEnum.OS_ERROR.value.get('code'),
                           msg=ResponseEnum.OS_ERROR.value.get('message'), content='')
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'), msg=ResponseEnum.SUCCESS.value.get('message'),
                       content='')


# 验证原手机号
@router.post('/mobile/validate')
async def validate_mobile(request: Request, mobile: str, code: str, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    _, hashed_token = auth_header.split(' ')
    if not auth_header or not hashed_token:
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    try:
        sub = auth_handler.decode_token(hashed_token)
    except Exception as e:
        logger.error(f'Error decoding token: {e}')
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    if not await request.app.state.redis.get(mobile):
        return my_response(result=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('message'),
                           content='')
    if not code == await request.app.state.redis.get(mobile):
        return my_response(result=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('message'),
                           content='')
    await request.app.state.redis.delete(mobile)
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'), msg=ResponseEnum.SUCCESS.value.get('message'),
                       content='')


# 更换手机号
@router.post('/mobile/rebind')
async def mobile_rebind(request: Request, mobile: str, code: str, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    _, hashed_token = auth_header.split(' ')
    if not auth_header or not hashed_token:
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    try:
        sub = auth_handler.decode_token(hashed_token)
    except Exception as e:
        logger.error(f'Error decoding token: {e}')
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    if not await request.app.state.redis.get(mobile):
        return my_response(result=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_EXPIRED.value.get('message'),
                           content='')
    if not code == await request.app.state.redis.get(mobile):
        return my_response(result=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('code'),
                           msg=ResponseEnum.VERIFICATION_CODE_ERROR.value.get('message'),
                           content='')
    user_id = sub.get('user_id')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return my_response(result=ResponseEnum.USER_NOT_EXIST.value.get('code'),
                           msg=ResponseEnum.USER_NOT_EXIST.value.get('message'), content='')
    try:
        user.mobile = mobile
        db.commit()
    except Exception as e:
        logger.error(f'{user.username} 更换手机号失败，{e}')
        db.rollback()
        return my_response(result=ResponseEnum.OS_ERROR.value.get('code'),
                           msg=ResponseEnum.OS_ERROR.value.get('message'), content='')
    await request.app.state.redis.delete(mobile)
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'), msg=ResponseEnum.SUCCESS.value.get('message'),
                       content='')


# 邮箱验证
@router.post('/email/validate')
async def validate_email(request: Request, email: str):
    auth_header = request.headers.get('Authorization')
    _, hashed_token = auth_header.split(' ')
    if not auth_header or not hashed_token:
        return my_response(result=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('code'),
                           msg=ResponseEnum.TOKEN_INVALID_OR_EXPIRED.value.get('message'), content='')
    try:
        sub = auth_handler.decode_token(hashed_token)
    except Exception as e:
        logger.error(f'Error decoding token: {e}')
    code = generate_verification_code()
    await request.app.state.redis.setex(name=email, value=code, time=60 * 5)
    return my_response(result=ResponseEnum.SUCCESS.value.get('code'), msg=ResponseEnum.SUCCESS.value.get('message'),
                       content='')
