from app.models import User
from app.services.base import BaseService


class UserService(BaseService):
    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        self.db.add(user)
        return self.commit_and_refresh(user)

    def list_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
