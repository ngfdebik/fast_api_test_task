from fastapi import FastAPI, HTTPException, status, Query, Response
from src.schemas import DepartmentsAddDTO, DepartmentsDTO, EmployeesAddDTO, EmployeesDTO
from src.db import session_factory
from src.queries.orm import SyncDepartmentORM, SyncEmployeeORM
from src.enums.deleteMode import DeleteMode
from src.logger.logger import setup_logger
import uvicorn


logger = setup_logger()
app = FastAPI()


@app.post("/departments/")
async def create_department(department: DepartmentsAddDTO):
    logger.info(f"POST /departments/ - Request: name='{department.name}', parent_id={department.parent_id}")
    try:
        with session_factory() as session:
            if department.parent_id is not None and not SyncDepartmentORM.department_id_exists(session, department.parent_id):
                logger.warning(f"Parent department not found: id={department.parent_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent department with id {department.parent_id} does not exist"
                )
            
            result = SyncDepartmentORM.create_department(session, department.name, department.parent_id)
            logger.info(f"Department created successfully: id={result.id}, name='{result.name}'")
            return DepartmentsDTO.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_department: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )



@app.post("/departments/{id}/employees")
async def create_employee(id: int, employee: EmployeesAddDTO):
    logger.info(f"POST /departments/{id}/employees - Request: full_name='{employee.full_name}', position='{employee.position}'")
    try:
        with session_factory() as session:
            logger.debug(f"Checking if department exists: id={id}")
            if not SyncDepartmentORM.department_id_exists(session, id):
                logger.warning(f"Department not found for employee creation: id={id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with id {id} does not exist"
                )
        
            result = SyncEmployeeORM.create_employee(
                session, 
                department_id=id,
                full_name=employee.full_name, 
                position=employee.position, 
                hired_at=employee.hired_at
            )
            logger.info(f"Employee created successfully: id={result.id}, department_id={id}")   
            return EmployeesDTO.model_validate(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_employee: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/departments/{id}")
async def get_departments(
    id: int, 
    depth: int = Query(1, ge=1, le=5, description="Глубина вложенных подразделений в ответе"),
    include_employees: bool = Query(True)):
        
        logger.info(f"GET /departments/{id} - Request: depth={depth}, include_employees={include_employees}")
        try:
            with session_factory() as session:
                logger.debug(f"Checking if department exists: id={id}")
                if not SyncDepartmentORM.department_id_exists(session, id):
                    logger.warning(f"Department not found for get request: id={id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Department with id {id} does not exist"
                    )
            
                result = SyncDepartmentORM.get_department(session, id, depth, include_employees)
                logger.info(f"Department retrieved successfully: id={id}, depth={depth}")
                return result
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_departments: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


@app.patch("/departments/{id}")
async def update_departments(id: int, department: DepartmentsAddDTO):
    logger.info(f"PATCH /departments/{id} - Request: name='{department.name}', parent_id={department.parent_id}")

    try:
        if id == department.parent_id:
            logger.warning(f"Attempt to set department as its own parent: id={id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department cannot be its own parent"
            )
        
        with session_factory() as session:
            logger.debug(f"Checking if department exists: id={id}")

            if not SyncDepartmentORM.department_id_exists(session, id):
                logger.warning(f"Department not found for update: id={id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with id {id} does not exist"
                )
            
            if department.parent_id is not None:
                logger.debug(f"Checking for circular dependency: ancestor={id}, descendant={department.parent_id}")
                if SyncDepartmentORM._is_descendant(
                    session, 
                    id,  
                    department.parent_id
                ):
                    logger.warning(f"Circular dependency detected: cannot set department {department.parent_id} as child of {id}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Cannot set department {department.parent_id} as parent because it is a descendant of department {id}"
                    )
            
            result = SyncDepartmentORM.update_department(
                session,
                department_id=id, 
                name=department.name, 
                parent_id=department.parent_id
            )

        logger.info(f"Department updated successfully: id={id}")
        return DepartmentsDTO.model_validate(result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_departments: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.delete("/departments/{id}")
async def delete_department(
    id: int,
    mode: DeleteMode = Query(..., description="Режим удаления: cascade или reassign"),
    reassign_to_department_id: int | None = Query(None, description="ID отдела для перевода сотрудников (обязателен при mode=reassign)")
):
    logger.warning(f"DELETE /departments/{id} - Request: mode={mode.value}, reassign_to={reassign_to_department_id}")

    try:
        with session_factory() as session:
            logger.debug(f"Checking if department exists: id={id}")
            if not SyncDepartmentORM.department_id_exists(session, id):
                logger.warning(f"Department not found for deletion: id={id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Department with id {id} does not exist"
                )
            
            if mode == DeleteMode.REASSIGN:
                if reassign_to_department_id is None:
                    logger.warning("reassign_to_department_id is missing for REASSIGN mode")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="reassign_to_department_id is required when mode=reassign"
                    )
            
                if reassign_to_department_id == id:
                    logger.warning(f"Attempt to reassign to same department: id={id}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot reassign employees to the same department being deleted"
                    )
                
                logger.debug(f"Checking if target department exists: id={reassign_to_department_id}")

                if not SyncDepartmentORM.department_id_exists(session, reassign_to_department_id):
                    logger.warning(f"Target department not found: id={reassign_to_department_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Department with id {reassign_to_department_id} does not exist"
                    )
                
                logger.info(f"Executing REASSIGN deletion: department={id} -> target={reassign_to_department_id}")
                
                SyncDepartmentORM.delete_department_reassign(session, id, reassign_to_department_id)
                logger.info(f"REASSIGN deletion completed: department={id}")

            elif mode == DeleteMode.CASCADE:
                logger.warning(f"Executing CASCADE deletion: department={id}")
                SyncDepartmentORM.delete_department_cascade(session, id)
                logger.info(f"CASCADE deletion completed: department={id}")

            logger.info(f"Department {id} deleted successfully")
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_department: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run("main:app", reload=True)