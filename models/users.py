import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    username = sa.Column(sa.String, nullable=True)
    carma = sa.Column(sa.Integer, autoincrement=True)