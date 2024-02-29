from fastapi.responses import JSONResponse
from app.enums.response_enums import ResponseEnum


def my_response(result=ResponseEnum.SUCCESS, msg='', content=''):
    if isinstance(result, int):
        code = result
    else:
        code = result.value
    if content == '':
        return JSONResponse(content={
            'code': code,
            'message': msg
        })
    else:
        return JSONResponse(content={
            'code': code,
            'message': msg,
            'data': content
        })
