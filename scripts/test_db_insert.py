from app.db.models.role import Role
from app.db.session import get_session, engine, Session
from app.db.models.user import User

db = get_session

addedUser = User(
    email="test2@example.com",
    name="test User",
    hashed_password="jfhadsf",
)

# Create a real session
with Session(engine) as db:
    db.add(addedUser)
    db.commit()

print("user inserted sucessfully")