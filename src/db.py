from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column
from sqlalchemy import create_engine, func, String
from src.config import settings
from typing import Annotated
import datetime



engine = create_engine(
    url=settings.DATABASE_URL_psycopg2,
    echo=False,
)

session_factory = sessionmaker(engine)

str_200 = Annotated[str, 200]
intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=func.now())]

class Base(DeclarativeBase):
    type_annotation_map = {
        str_200: String(200)
    }

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"
