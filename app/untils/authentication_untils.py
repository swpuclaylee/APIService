import random
import logging
import phonenumbers

from datetime import datetime, timedelta
from twilio.rest import Client
from fastapi import Request
from phonenumbers import PhoneNumberFormat
from sqlalchemy.orm import Session
from typing import Tuple
from app.core.config import TWILIO_SID, TWILIO_PHONE_NUMBER, TWILIO_TOKEN, message_body
from app.core.config import log_name
from app.untils.reponse_untils import my_response
from app.enums.response_enums import ResponseEnum

logger = logging.getLogger(log_name)

client = Client(TWILIO_SID, TWILIO_TOKEN)


# 生成国际格式手机号码
def generate_international_mobile(mobile: str) -> str:
    """
    生成国际格式手机号码
    :param mobile: 手机号
    :return: str
    """
    default_region = "CN"
    parsed_mobile = phonenumbers.parse(mobile, default_region)
    international_mobile = phonenumbers.format_number(parsed_mobile, PhoneNumberFormat.INTERNATIONAL)
    return international_mobile


# 生成4位数验证码
def generate_verification_code() -> str:
    """
    生成4位数验证码
    :return: str
    """
    code_list = []
    for i in range(10):
        code_list.append(str(i))
    temp_slice = random.sample(code_list, 4)
    verification_code = ''.join(temp_slice)
    return verification_code


# 发送短信
async def send_sms_to_number(request: Request, mobile: str) -> bool:
    """
    发送短信
    :param mobile: 手机号
    :param request: 请求对象
    :return: bool
    """
    client_ip = request.client.host
    cache_mobile = await request.app.state.redis.get(mobile)
    if cache_mobile:
        return my_response(result=ResponseEnum.SMS_SEND_FREQUENT.value.get('code'),
                           msg=ResponseEnum.SMS_SEND_FREQUENT.value.get('message'), content='')
    verification_code = generate_verification_code()
    international_mobile = generate_international_mobile(mobile)
    try:
        today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        timeout_seconds = (today_midnight - datetime.now()).seconds
        sms_mobile_count = await request.app.state.redis.get(f'sms:limit:{mobile}')
        if sms_mobile_count:
            sms_mobile_count = int(sms_mobile_count) + 1
            await request.app.state.redis.setex(name=f'sms:limit:{mobile}', value=sms_mobile_count,
                                                time=timeout_seconds)
        else:
            await request.app.state.redis.setex(name=f'sms:limit:{mobile}', value=1, time=timeout_seconds)
        sms_ip_count = await request.app.state.redis.get(f'sms:limit:{client_ip}')
        if sms_ip_count:
            sms_ip_count = int(sms_ip_count) + 1
            await request.app.state.redis.setex(name=f'sms:limit:{client_ip}', value=sms_ip_count,
                                                time=timeout_seconds)
        else:
            await request.app.state.redis.setex(name=f'sms:limit:{client_ip}', value=1, time=timeout_seconds)
        await request.app.state.redis.setex(name=mobile, value=verification_code, time=300)
        message = client.messages.create(
            body=message_body.format(verification_code),
            from_=TWILIO_PHONE_NUMBER,
            to=international_mobile
        )
        logger.info(f'发送短信成功，手机号为{mobile}，验证码为{verification_code}')
        return my_response(result=ResponseEnum.SUCCESS.value.get('code'),
                           msg=ResponseEnum.SUCCESS.value.get('message'), content='')
    except Exception as e:
        logger.error(f'发送短信失败，手机号为{mobile}，验证码为{verification_code}. 原因：{e}')
        return my_response(result=ResponseEnum.SMS_SEND_FAILED.value.get('code'),
                           msg=ResponseEnum.SMS_SEND_FAILED.value.get('message'), content='')

