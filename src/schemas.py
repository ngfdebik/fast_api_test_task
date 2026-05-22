import datetime
from pydantic import BaseModel, ConfigDict

class DepartmentsAddDTO(BaseModel):
    name: str
    parent_id: int | None

    model_config = ConfigDict(from_attributes=True)

class DepartmentsDTO(DepartmentsAddDTO):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeesAddDTO(BaseModel):
    department_id: int
    full_name: str
    position: str
    hired_at: datetime.date | None

    model_config = ConfigDict(from_attributes=True)

class EmployeesDTO(EmployeesAddDTO):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class DepartmentsRelDTO(DepartmentsDTO):
    employees: list["EmployeesDTO"]
    children: list["DepartmentsDTO"]
    parent: "DepartmentsDTO"

    model_config = ConfigDict(from_attributes=True)

class EmployeesRelDTO(EmployeesDTO):
    department: "DepartmentsDTO"

    model_config = ConfigDict(from_attributes=True)