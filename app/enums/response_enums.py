from enum import Enum, unique


@unique
class ResponseEnum(Enum):
    SUCCESS = {
        'code': 0,
        'message': '成功'
    }
    USERNAME_OR_PASSWORD_ERROR = {
        'code': 1001,
        'message': '用户名或密码错误'
    }
    USER_NOT_EXIST = {
        'code': 1002,
        'message': '用户不存在'
    }
    ACCOUNT_FORBIDDEN = {
        'code': 1003,
        'message': '账号已禁用'
    }
    ACCOUNT_EXPIRED = {
        'code': 1004,
        'message': '账号已过期'
    }
    ACCOUNT_LOCKED = {
        'code': 1005,
        'message': '账号已锁定'
    }
    TOKEN_EXPIRED = {
        'code': 1006,
        'message': 'token已过期'
    }
    ACCESS_NOT_ALLOWED = {
        'code': 1007,
        'message': '不允许访问'
    }
    NO_ACCESS = {
        'code': 1008,
        'message': '无访问权限'
    }
    TOKEN_INVALID_OR_EXPIRED = {
        'code': 1009,
        'message': 'token无效或已过期'
    }
    REFRESH_TOKEN_INVALID_OR_EXPIRED = {
        'code': 1010,
        'message': 'refresh token无效或已过期'
    }
    INVALID_REQUEST_OR_REQUEST_NOT_ACCEPTED = {
        'code': 1011,
        'message': '请求无效或请求未被接受'
    }
    INTERFACE_ACCESS_LIMIT = {
        'code': 1012,
        'message': '接口访问限制'
    }
    OS_ERROR = {
        'code': 1013,
        'message': '系统错误'
    }
    SMS_SEND_FAILED = {
        'code': 1014,
        'message': '发送失败, 请稍后尝试'
    }
    SMS_SEND_FREQUENT = {
        'code': 1015,
        'message': '发送太频繁！请稍后尝试'
    }
    SMS_EXCEEDING_LIMIT = {
        'code': 1016,
        'message': '发送次数超过限制，请明日在尝试'
    }
    USER_ALREADY_EXISTS = {
        'code': 1017,
        'message': '用户已存在'
    }
    VERIFICATION_CODE_EXPIRED = {
        'code': 1018,
        'message': '验证码已过期'
    }
    VERIFICATION_CODE_ERROR = {
        'code': 1019,
        'message': '验证码错误'
    }
    REGISTRATION_FAILED = {
        'code': 1020,
        'message': '注册失败，请稍后尝试'
    }
    USER_NAME_ALREADY_EXISTS = {
        'code': 1021,
        'message': '用户名已存在'
    }