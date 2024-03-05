from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa 
import sqlalchemy.orm as so

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return '<Post {}>'.format(self.body)
    
class Thing(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    code_name: so.Mapped[str] = so.mapped_column(sa.String(140), unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[str] = so.mapped_column(sa.Text())
    location_name: so.Mapped[str] = so.mapped_column(sa.String(140))

    histories: so.WriteOnlyMapped['History'] = so.relationship(
        back_populates='thing',
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return '<User {}>'.format(self.code_name)

class History(db.Model):
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    lat: so.Mapped[float] = so.mapped_column(sa.Float())
    lng: so.Mapped[float] = so.mapped_column(sa.Float())
    gas: so.Mapped[float] = so.mapped_column(sa.Float())
    temperature: so.Mapped[float] = so.mapped_column(sa.Float())
    humidity: so.Mapped[float] = so.mapped_column(sa.Float())
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    thing_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Thing.id), index=True)

    thing: so.Mapped[Thing] = so.relationship(back_populates='histories')

class Action(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(140))
    thing_code: so.Mapped[str] = so.mapped_column(sa.String(140))
    type: so.Mapped[str] = so.mapped_column(sa.String(140))
    destination: so.Mapped[str] = so.mapped_column(sa.String(140))
    field: so.Mapped[str] = so.mapped_column(sa.String(140))
    operation: so.Mapped[str] = so.mapped_column(sa.String(140))

    value: so.Mapped[float] = so.mapped_column(sa.Float())


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))