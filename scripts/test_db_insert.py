from app.db.models.role import Role
from app.db.session import SessionLocal
from app.db.models.user import User

db = SessionLocal()

addedUser = User(
    email="test@example",
    role_id=1,
    name="test User",
    password_hash="jfhadsf",
)

db.add(addedUser)
db.commit()

print("user inserted sucessfully")