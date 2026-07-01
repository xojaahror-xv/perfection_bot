from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    current_lesson = Column(Integer, default=1)
    is_vip = Column(Boolean, default=False)
    joined_from = Column(String, default="organic")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_user(telegram_id: int):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    session.close()
    return user

def create_user(telegram_id: int, username: str, joined_from: str = "organic"):
    session = SessionLocal()
    user = User(telegram_id=telegram_id, username=username, joined_from=joined_from)
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user

def update_user_lesson(telegram_id: int, lesson_num: int):
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.current_lesson = lesson_num
        session.commit()
    session.close()
