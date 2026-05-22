from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base, intpk, created_at, str_200
import datetime



class DepartmensORM(Base):
    __tablename__ = "departmens"

    id: Mapped[intpk]
    name: Mapped[str_200]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("departmens.id", ondelete="CASCADE"))
    created_at: Mapped[created_at]


    employees: Mapped[list["EmployeesORM"]] = relationship(back_populates="department")
    parent: Mapped["DepartmensORM | None"] = relationship(
        back_populates="children",
        remote_side="DepartmensORM.id"
    )
    children: Mapped[list["DepartmensORM"]] = relationship(
        back_populates="parent"
    )

    repr_cols_num = 3

class EmployeesORM(Base):
    __tablename__ = "employees"

    id: Mapped[intpk]
    department_id: Mapped[int] = mapped_column(ForeignKey("departmens.id", ondelete="CASCADE"))
    full_name: Mapped[str_200]
    position: Mapped[str_200]
    hired_at: Mapped[datetime.date | None]
    created_at: Mapped[created_at]

    department: Mapped["DepartmensORM"] = relationship(back_populates="employees")

    repr_cols_num = 5