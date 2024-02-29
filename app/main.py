from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger_config import configure_logging
from app.blog.user import user
from app.blog.authentication import authentication
from app.db.redis import register_redis

app = FastAPI()

# 挂载路由
app.include_router(user.router, prefix='/api/user', tags=['用户'])
app.include_router(authentication.router, prefix='/api/authentication', tags=['认证'])

# 配置日志
configure_logging()

# 前后端跨域
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 挂载 redis
register_redis(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host='0.0.0.0', port=8000, reload=True)
