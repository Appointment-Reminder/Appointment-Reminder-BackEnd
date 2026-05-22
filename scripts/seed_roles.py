from app.db.session import SessionLocal
from app.db.models.role import Role

db = SessionLocal()

roles = ["owner", "admin", "viewer"]

for role_name in roles:
    existing = db.query(Role).filter(Role.name == role_name).first()
    if not existing:
        db.add(Role(name=role_name))


db.commit()
print("Roles seeded successfully")