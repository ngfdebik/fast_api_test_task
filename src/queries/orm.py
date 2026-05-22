from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models import DepartmensORM, EmployeesORM
from src.logger.logger import setup_logger
import datetime

logger = setup_logger()

class SyncDepartmentORM:
    @staticmethod
    def create_department(session: Session, name: str, parent_id: int | None = None) -> DepartmensORM:
        logger.info(f"Creating department: name='{name}', parent_id={parent_id}")
        try:
            department = DepartmensORM(
                name=name,
                parent_id=parent_id
            )
            session.add(department)
            session.commit()
            session.refresh(department)
            logger.info(f"Department created successfully: id={department.id}, name='{department.name}'")
            return department
        except Exception as e:
            logger.error(f"Failed to create department: name='{name}', parent_id={parent_id}, error={e}", exc_info=True)
            raise
    
    @staticmethod
    def update_department(session: Session, department_id:int, name: str | None, parent_id: int | None = None) -> DepartmensORM:
        logger.info(f"Updating department: id={department_id}, name={name}, parent_id={parent_id}")
        try:
            department = session.get(DepartmensORM, department_id)
            if not department:
                logger.warning(f"Department not found for update: id={department_id}")
                raise ValueError(f"Department with id {department_id} not found")
            
            old_name = department.name
            old_parent_id = department.parent_id
            
            if name is not None:
                logger.debug(f"Changing name from '{old_name}' to '{name}'")
                department.name = name

            if parent_id is not None:
                logger.debug(f"Changing parent_id from {old_parent_id} to {parent_id}")
                department.parent_id = parent_id
            
            session.commit()
            session.refresh(department)
            logger.info(f"Department updated successfully: id={department_id}, changes: name={old_name}->{department.name}, parent_id={old_parent_id}->{department.parent_id}")
            return department
        except Exception as e:
            logger.error(f"Failed to update department: id={department_id}, error={e}", exc_info=True)
            raise
    
    @staticmethod
    def _is_descendant(session: Session, ancestor_id: int, descendant_id: int) -> bool:
        logger.debug(f"Checking if department {descendant_id} is descendant of {ancestor_id}")
        try:
            descendants_cte = select(
                DepartmensORM.id
            ).where(
                DepartmensORM.parent_id == ancestor_id
            ).cte(recursive=True)
            
            descendants_cte = descendants_cte.union_all(
                select(DepartmensORM.id).where(
                    DepartmensORM.parent_id == descendants_cte.c.id
                )
            )
            
            query = select(descendants_cte).where(descendants_cte.c.id == descendant_id)
            result = session.execute(query).first()

            is_desc = result is not None
            if is_desc:
                logger.debug(f"Department {descendant_id} IS a descendant of {ancestor_id}")
            else:
                logger.debug(f"Department {descendant_id} is NOT a descendant of {ancestor_id}")
            
            return is_desc
        except Exception as e:
            logger.error(f"Error checking descendant relationship: ancestor={ancestor_id}, descendant={descendant_id}, error={e}", exc_info=True)
            raise

    
    @staticmethod
    def get_department(session, department_id: int, depth: int = 1, include_employees: bool = True):
        logger.info(f"Getting department: id={department_id}, depth={depth}, include_employees={include_employees}")
        
        department = session.query(DepartmensORM).filter(DepartmensORM.id == department_id).first()
        if not department:
            logger.warning(f"Department not found: id={department_id}")
            return None
        
        result = {
            "department":{
                "id": department.id,
                "name": department.name,
                "parent_id": department.parent_id,
                "created_at": department.created_at,
            },
            "children": [],  
            "employees": [] 
        }
        
        if include_employees:
            employees_list = list(department.employees)
            employees_list.sort(key=lambda x: (x.created_at, x.full_name))
            result["employees"] = [
                {
                    "id": emp.id,
                    "full_name": emp.full_name,
                    "position": emp.position,
                    "hired_at": emp.hired_at,
                    "department_id": emp.department_id,
                    "created_at": emp.created_at
                }
                for emp in employees_list
            ]
        
        if depth > 1:
            for child in department.children:
                child_data = SyncDepartmentORM.get_department(
                    session, child.id, depth - 1, include_employees
                )
                if child_data:
                    result["children"].append(child_data)
        else:
            for child in department.children:
                result["children"].append({
                    "id": child.id,
                    "name": child.name,
                    "parent_id": child.parent_id,
                    "created_at": child.created_at,
                    "employees": [] if not include_employees else [
                        {
                            "id": emp.id,
                            "full_name": emp.full_name,
                            "position": emp.position,
                            "hired_at": emp.hired_at,
                            "department_id": emp.department_id,
                            "created_at": emp.created_at
                        }
                        for emp in child.employees
                    ] if include_employees else [],
                    "children": [],
                })
        
        logger.info(f"Department {department_id} retrieved successfully")
        return result
    
    @staticmethod
    def delete_department_cascade(session: Session, department_id: int):
        logger.warning(f"Executing CASCADE delete for department: id={department_id}")
        try:
            department = session.get(DepartmensORM, department_id)
            if not department:
                logger.warning(f"Department not found for cascade delete: id={department_id}")
                return
            
            employee_count = session.query(EmployeesORM).filter(
                EmployeesORM.department_id == department_id
            ).count()
            logger.debug(f"Department {department_id} has {employee_count} direct employees")
            
            child_count = session.query(DepartmensORM).filter(
                DepartmensORM.parent_id == department_id
            ).count()
            logger.debug(f"Department {department_id} has {child_count} direct child departments")

            session.delete(department)
            session.commit()
            logger.info(f"CASCADE delete completed for department {department_id}: deleted {employee_count} employees and {child_count} child departments")
        except Exception as e:
            logger.error(f"Error during cascade delete for department {department_id}: {e}", exc_info=True)
            session.rollback()
            raise

    @staticmethod
    def delete_department_reassign(session: Session, department_id: int, target_department_id: int):
        logger.warning(f"Executing REASSIGN delete for department: id={department_id}, target={target_department_id}")
        try:
            employee_count = session.query(EmployeesORM).filter(
                EmployeesORM.department_id == department_id
            ).count()
            logger.info(f"Reassigning {employee_count} employees from department {department_id} to {target_department_id}")

            if employee_count > 0:
                session.query(EmployeesORM).filter(
                    EmployeesORM.department_id == department_id
                ).update(
                    {EmployeesORM.department_id: target_department_id},
                    synchronize_session=False
                )
                logger.debug(f"Employees reassigned successfully")

            children_count = session.query(DepartmensORM).filter(
                DepartmensORM.parent_id == department_id
            ).count()
            logger.info(f"Moving {children_count} child departments from {department_id} to {target_department_id}")
            
            if children_count > 0:
                session.query(DepartmensORM).filter(
                    DepartmensORM.parent_id == department_id
                ).update(
                    {DepartmensORM.parent_id: target_department_id},
                    synchronize_session=False
                )
                logger.debug(f"Child departments moved successfully")

            logger.debug(f"Deleting department {department_id}")
            department = session.get(DepartmensORM, department_id)
            if department:
                session.delete(department)

            session.commit()
            logger.info(f"REASSIGN delete completed for department {department_id}: reassigned {employee_count} employees, moved {children_count} children")
        except Exception as e:
            logger.error(f"Error during reassign delete for department {department_id}: {e}", exc_info=True)
            session.rollback()
            raise
    
    @staticmethod
    def department_id_exists(session, department_id: int) -> bool:
        try:
            logger.debug(f"Checking if department exists: id={department_id}")
            department = session.get(DepartmensORM, department_id)
            exists = department is not None
            logger.debug(f"Department {department_id} exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking department existence: id={department_id}, error={e}", exc_info=True)
            return False


class SyncEmployeeORM:
    @staticmethod
    def create_employee(session: Session, department_id: int, full_name: str, position: str, hired_at: datetime.date | None = None) -> EmployeesORM:
        logger.info(f"Creating employee: department_id={department_id}, full_name='{full_name}', position='{position}', hired_at={hired_at}")
        try:
            employee = EmployeesORM(
                department_id=department_id,
                full_name=full_name,
                position=position,
                hired_at=hired_at
            )
            session.add(employee)
            session.commit()
            session.refresh(employee)
            logger.info(f"Employee created successfully: id={employee.id}, full_name='{employee.full_name}'")
            return employee
        except Exception as e:
            logger.error(f"Failed to create employee: department_id={department_id}, full_name='{full_name}', error={e}", exc_info=True)
            raise
        