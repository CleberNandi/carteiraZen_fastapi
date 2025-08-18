from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all models in the application.
    This class is used to define the base for SQLAlchemy ORM models.
    It inherits from DeclarativeBase, which provides the necessary functionality
    to create and manage database tables.
    """

    pass
