from fastapi import FastAPI, Request
from sqlalchemy.orm import configure_mappers
from starlette.responses import JSONResponse

from app.services.errors.BusinessErrors import UserAlreadyMemberOfBusiness, InvalidBusinessAuthorization, \
    InvalidBusiness, BusinessAlreadyExists, UserNotFoundInBusiness, OwnerRoleEditing, MemberRemoval
from app.services.errors.error_base import ServiceError
from app.services.errors.user_errors import UserNotFound


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ServiceError)
    async def handle_service_error(
            request: Request,
            exc: ServiceError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserNotFound)
    async def handle_user_not_found(
            request: Request,
            exc: UserNotFound,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidBusinessAuthorization)
    async def handle_invalid_business_authorization(
            request: Request,
            exc: InvalidBusinessAuthorization,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidBusiness)
    async def handle_invalid_business(
            request: Request,
            exc: InvalidBusiness,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(BusinessAlreadyExists)
    async def handle_business_already_exists(
            request: Request,
            exc: BusinessAlreadyExists,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserAlreadyMemberOfBusiness)
    async def handle_user_already_member_of_business(
            request: Request,
            exc: UserAlreadyMemberOfBusiness,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserNotFoundInBusiness)
    async def handle_user_not_found(
            request: Request,
            exc: UserNotFound,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(OwnerRoleEditing)
    async def handle_invalid_business(
            request: Request,
            exc: OwnerRoleEditing,
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(MemberRemoval)
    async def handle_member_removal(
            request: Request,
            exc: MemberRemoval,
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )




