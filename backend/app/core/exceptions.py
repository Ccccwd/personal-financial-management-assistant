"""
异常处理
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, code: int = 400, message: str = "请求错误", data: any = None):
        self.code = code
        self.message = message
        self.data = data


def setup_exception_handlers(app):
    """设置异常处理器"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": exc.data
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 422,
                "message": "参数校验失败",
                "data": {"errors": errors}
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 500,
                "message": "数据库操作错误",
                "data": str(exc) if app.debug else None
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": str(exc) if app.debug else None
            }
        )
