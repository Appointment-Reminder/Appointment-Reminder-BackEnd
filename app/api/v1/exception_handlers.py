from fastapi import FastAPI, Request
from sqlalchemy.orm import configure_mappers
from starlette.responses import JSONResponse

from app.domain.business.errors.business_errors import BusinessError
from app.domain.core.errors.errors import DomainError
from app.domain.user.errors.user_errors import UserError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_service_error(
            request: Request,
            exc: DomainError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserError)
    async def handle_user_not_found(
            request: Request,
            exc: UserError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BusinessError)
    async def handle_invalid_business_authorization(
            request: Request,
            exc: BusinessError,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BusinessError)
    async def handle_invalid_business(
            request: Request,
            exc: BusinessError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BusinessError)
    async def handle_business_already_exists(
            request: Request,
            exc: BusinessError,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserError)
    async def handle_user_already_member_of_business(
            request: Request,
            exc: UserError,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserError)
    async def handle_user_not_found(
            request: Request,
            exc: UserError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserError)
    async def handle_invalid_business(
            request: Request,
            exc: UserError,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserError)
    async def handle_member_removal(
            request: Request,
            exc: UserError,
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )




