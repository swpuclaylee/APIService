# 日志名称
log_name = 'app_log'

# 数据所在数据库信息
DATABASE_URL = 'mysql+pymysql://root:root@localhost/blog?charset=utf8mb4'

# twilio sms配置
TWILIO_SID = 'ACd9265533ead59926fa7cff7a262b2991'
TWILIO_TOKEN = '7e1be6ae95cc39dbaf00ad0092deef25'
TWILIO_PHONE_NUMBER = '+12512200453'

# 短信格式
message_body = "【clay's blog】尊敬的用户，您的验证码为：{}，请在5分钟内完成验证。"

# 短信最大发送次数
SMS_DAILY_LIMIT = 1000

# 密钥
SECRET_KEY = 'SvaqLLAbeB4T4dx_hg-ffH34pg5SXgzyBGystf1jsPQ'

# 不需要token验证的接口
NO_TOKEN_URLS = [
    '/sms/send',
    '/account/login',
    '/mobile/login',
    '/oauth',
    '/refresh_access_token',
    '/logout',
    '/user/register',
    '/user/password/reset',
    '/user/email/bind',
    '/tag/list',
    '/category/list',
    '/article/published/page',
    '/article/view/{id}',
    '/increment_view/{id}',
    '/article/interrelated/list',
    '/article/archives/page',
    '/article/tag/statistic',
    '/article/category/statistic',
    '/article/recommend/list',
    '/article/comment/page',
    '/article/comment/latest',
    '/leave/message/page',
    '/leave/message/latest',
    '/friend/link/page',
    '/friend/link/list'
]

# 邮件发送配置
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 25
MAIL_USERNAME = 'clay0087blog@163.com'
MAIL_PASSWORD = 'KZHJFMWYSYONYZSZ'
VALIDATE_MAIL_SUBJECT = "clay's blog 邮箱验证"
VALIDATE_MAIL_BODY = "Hello, this is a  email from clay! 你的验证码是{}，5分钟之内有效。"
