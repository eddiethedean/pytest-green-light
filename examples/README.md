# Integration Examples

This directory contains practical examples of using `pytest-green-light` with various frameworks and scenarios.

## FastAPI Example

The `fastapi_example.py` file demonstrates:

- Setting up async SQLAlchemy engines and sessions with pytest-green-light
- Using transaction management for test isolation
- Testing FastAPI applications with async database operations
- Nested transactions for complex test scenarios

### Running the Example

```bash
# Install dependencies
pip install fastapi pytest-asyncio aiosqlite

# Run the example tests
pytest examples/fastapi_example.py -v
```

## Usage Patterns

### Pattern 1: Basic Engine and Session

```python
from pytest_green_light.fixtures import async_engine_factory, async_session_factory

@pytest.fixture
async def engine():
    async for eng in async_engine_factory("sqlite+aiosqlite:///:memory:"):
        yield eng

@pytest.fixture
async def session(engine):
    async for sess in async_session_factory(engine):
        yield sess
```

### Pattern 2: Transaction Management

```python
from pytest_green_light.fixtures import async_db_transaction

async def test_with_rollback(session):
    async with async_db_transaction(session):
        # All changes automatically rolled back
        session.add(obj)
        await session.commit()
```

### Pattern 3: Nested Transactions

```python
async def test_nested_transactions(session):
    # Create base data
    async with async_db_transaction(session, rollback=False):
        session.add(base_obj)
        await session.commit()
    
    # Nested transaction that gets rolled back
    async with async_db_transaction(session, nested=True, rollback=True):
        session.add(test_obj)
        await session.commit()
```

## Real-World Scenarios

### Scenario 1: Testing Repository Patterns

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        await self.session.commit()
        return user

async def test_user_repository(session):
    async with async_db_transaction(session):
        repo = UserRepository(session)
        user = await repo.create_user("Alice", "alice@example.com")
        assert user.name == "Alice"
```

### Scenario 2: Testing Service Layers

```python
class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def register_user(self, name: str, email: str) -> User:
        # Complex business logic
        user = User(name=name, email=email)
        self.session.add(user)
        await self.session.flush()
        # More business logic...
        await self.session.commit()
        return user

async def test_user_service(session):
    async with async_db_transaction(session):
        service = UserService(session)
        user = await service.register_user("Alice", "alice@example.com")
        assert user.id is not None
```

### Scenario 3: Testing API Endpoints

```python
from fastapi import Depends
from fastapi.testclient import TestClient

def get_db():
    # Dependency injection for session
    pass

@app.post("/users")
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    user = User(**user_data)
    db.add(user)
    await db.commit()
    return user

async def test_create_user_endpoint(client, session):
    async with async_db_transaction(session):
        response = client.post("/users", json={"name": "Alice", "email": "alice@example.com"})
        assert response.status_code == 200
```

## Best Practices

1. **Always use transaction management** for test isolation
2. **Use nested transactions** when you need to test partial rollbacks
3. **Set up fixtures** at the module or session level for performance
4. **Use factory functions** when you need multiple engines or sessions
5. **Enable debug mode** (`--green-light-debug`) when troubleshooting

## Troubleshooting

If you encounter `MissingGreenlet` errors:

1. Ensure `pytest-green-light` is installed
2. Verify the plugin is loaded: `pytest --version`
3. Run with `--green-light-debug` for diagnostics
4. Check that you're using async fixtures and test functions
5. Ensure `pytest-asyncio` is installed if using async tests

