import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

mock_logger = MagicMock()
mock_setup_logger = MagicMock(return_value=mock_logger)

import src.logger.logger
src.logger.logger.setup_logger = mock_setup_logger
src.logger.logger.logger = mock_logger

from app.main import app
from src.db import Base
from src.db import session_factory as original_session_factory

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    import src.db
    original_factory = src.db.session_factory
    
    def get_test_session():
        return session
    
    src.db.session_factory = get_test_session
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
    
    src.db.session_factory = original_factory

@pytest.fixture(scope="function")
def client(db_session):
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def sample_department(db_session):
    from src.queries.orm import SyncDepartmentORM
    
    department = SyncDepartmentORM.create_department(
        db_session, 
        "Test Department", 
        None
    )
    db_session.commit()  # Важно: коммитим
    return department

@pytest.fixture(scope="function")
def sample_employee(sample_department, db_session):
    from src.queries.orm import SyncEmployeeORM
    from datetime import date
    
    employee = SyncEmployeeORM.create_employee(
        db_session,
        sample_department.id,
        "John Doe",
        "Developer",
        date.today()
    )
    db_session.commit()
    return employee