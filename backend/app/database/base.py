"""
SQLAlchemy declarative base.

All ORM models inherit from `Base`. Importing every model module here (or in
main.py) ensures they're registered on Base.metadata before `create_all` runs.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
