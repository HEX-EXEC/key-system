import sys
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.sql import text
from passlib.context import CryptContext

DATABASE_URL = "postgresql://keydb_sosk_user:dGGWuBlOdnuj11xmxwJt4xXzYZEiqpnP@dpg-cv3l3cpu0jms73aj2gh0-a.oregon-postgres.render.com/keydb_sosk"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    print("Dropped users table.")
    conn.commit()

User.__table__.create(bind=engine)
print("Created users table with correct schema.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_admin_user():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("Admin user already exists.")
            return
        hashed_password = get_password_hash("securepassword123")
        admin_user = User(
            username="admin",
            hashed_password=hashed_password,
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()