from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True, doc='用户名')
    password = Column(String(100), nullable=False, doc='密码')
    mobile = Column(String(100), index=True, unique=True, nullable=False, doc='手机号')
    nickname = Column(String(100), doc='昵称')
    gender = Column(Integer, doc='性别，0：女，1：男')
    birthday = Column(DateTime, doc='生日')
    email = Column(String(100), unique=True, index=True, doc='邮箱')
    brief = Column(String(100), doc='个性签名')
    avatar = Column(String(100), doc='头像')
    status = Column(Integer, default=0, doc='用户状态，0代表正常，1代表锁定，2代表禁用，3代表过期')
    admin = Column(Integer, default=0, doc='是否管理员，1：是，0：否')
    create_time = Column(DateTime(timezone=True), server_default=func.now(), doc='注册时间')
