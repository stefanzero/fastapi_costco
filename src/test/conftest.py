from contextlib import ExitStack
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# from src.main import app as actual_app
from src.main import app
from src.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )

# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(bind=engine)


# def override_get_db() -> Generator[Session, None, None]:
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# actual_app.dependency_overrides[get_db] = override_get_db
@pytest.fixture(scope="function")
# def db_session(db_url=SQLALCHEMY_DATABASE_URL):
def db(db_url=SQLALCHEMY_DATABASE_URL):
    """Create a new database session with a rollback at the end of the test."""
    # Create a SQLAlchemy engine
    engine = create_engine(
        db_url,
        # connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create a sessionmaker to manage sessions
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables in the database
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# @pytest.fixture(scope="session", autouse=True)
# def app(db_session):
#     with ExitStack():
#         actual_app.dependency_overrides[get_db] = override_get_db
#         teardown()
#         setup()
#         yield actual_app


# @pytest.fixture
# def client(app) -> Generator[TestClient, None, None]:
#     with TestClient(app) as c:
#         yield c


@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


# def setup() -> None:
#     # Create the tables in the test database
#     Base.metadata.create_all(bind=engine)


# def teardown() -> None:
#     # Drop the tables in the test database
#     Base.metadata.drop_all(bind=engine)


""" 
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def run_migrations(connection: Connection):
    config = Config("app/alembic.ini")
    config.set_main_option("script_location", "app/alembic")
    config.set_main_option("sqlalchemy.url", settings.database_url)
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs("head", rev)

    context = MigrationContext.configure(connection, opts={"target_metadata": Base.metadata, "fn": upgrade})

    with context.begin_transaction():
        with Operations.context(context):
            context.run_migrations()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Run alembic migrations on test DB
    async with sessionmanager.connect() as connection:
        await connection.run_sync(run_migrations)

    yield

    # Teardown
    await sessionmanager.close()


# Each test function is a clean slate
@pytest.fixture(scope="function", autouse=True)
async def transactional_session():
    async with sessionmanager.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            await session.rollback()  # Rolls back the outer transaction


@pytest.fixture(scope="function")
async def db_session(transactional_session):
    yield transactional_session


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, db_session):
    async def get_db_session_override():
        yield db_session[0]

    app.dependency_overrides[get_db_session] = get_db_session_override


"""


# @pytest.fixture(scope="function", autouse=True)
# def db() -> Session:
#     return next(override_get_db())
