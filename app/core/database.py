from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建mysql连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
