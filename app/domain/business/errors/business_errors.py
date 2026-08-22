from app.domain.core.errors.errors import DomainError

class BusinessError(DomainError):
    """Business Error Base class"""

class InvalidBusinessAuthorization(BusinessError):
    def __init__(self, business_id: int) -> None:
        super().__init__(
            f"You don't have permission to access this business {business_id}"
        )
        self.business_id = business_id

class InvalidBusiness(BusinessError):
    def __init__(self, business_id: int) -> None:
        super().__init__(
            f"Business {business_id} doesn't exist"
        )
        self.business_id = business_id

class BusinessAlreadyExists(BusinessError):
    def __init__(self, business_name: str) -> None:
        super().__init__(
            f"Business {business_name} already exists"
        )
        self.business_name = business_name

class UserAlreadyMemberOfBusiness(BusinessError):
    def __init__(self, user_id):
        super().__init__(
            f"User {user_id} already member"
        )
        self.user_id = user_id

class UserNotFoundInBusiness(BusinessError):
    def __init__(self, user_id, business_id):
        super().__init__(
            f"User {user_id} doesn't exist in business {business_id}"
        )
        self.user_id = user_id
        self.business_id = business_id

class OwnerRoleEditing(BusinessError):
    def __init__(self, user_id, business_id):
        super().__init__(
            f"User {user_id} doesn't have permission to edit owner role in business {business_id}"
        )
        self.user_id = user_id
        self.business_id = business_id

class MemberRemoval(BusinessError):
    def __init__(self, user_id: int, removed_id: int, business_id: int):
        super().__init__(
            f"User {user_id} doesn't have permission to remove {removed_id} from business {business_id}"
        )

class UnauthorizedBusinessAction(BusinessError):
    def __init__(self, user_id: int, business_id: int):
        super().__init__(
            f"User {user_id} doesn't have permission for business {business_id}"
        )
        self.user_id = user_id
        self.business_id = business_id