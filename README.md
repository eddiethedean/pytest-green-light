# pytest-green-light

A pytest plugin that gives SQLAlchemy async engines the green light to work seamlessly in pytest fixtures. Solves the `MissingGreenlet` error automatically.

> ✅ **Status: Working (Alpha)**  
> **Version:** 0.1.0
> 
> This package is functional and ready to use! It automatically establishes greenlet context for SQLAlchemy async engines in pytest fixtures.

## The Problem

SQLAlchemy's async engines require a greenlet context to be established before async operations can be performed. When using pytest fixtures with async SQLAlchemy code, you encounter:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
```

This happens because pytest's async fixtures don't automatically establish the greenlet context that SQLAlchemy async requires.

## The Solution

This plugin automatically establishes greenlet context before async tests run, allowing SQLAlchemy async engines to work seamlessly in pytest fixtures. Just install it and your async SQLAlchemy tests will work!

## Installation

```bash
pip install pytest-green-light
```

## Usage

### Basic Usage

Just install the plugin and use async SQLAlchemy in your tests:

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    yield engine
    await engine.dispose()

@pytest.fixture
async def async_session(async_engine):
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session

async def test_my_async_code(async_session):
    # This works now! No more MissingGreenlet errors
    from sqlalchemy import text
    result = await async_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
```

### With pytest-asyncio

This plugin works alongside `pytest-asyncio`:

```bash
pip install pytest-asyncio pytest-green-light
```

```python
import pytest

pytestmark = pytest.mark.asyncio

async def test_async_sqlalchemy(async_session):
    # Works perfectly!
    pass
```

### Helper Fixtures

The plugin provides convenient fixtures for common patterns:

```python
from pytest_green_light.fixtures import (
    async_engine_factory,
    async_session_factory,
    async_db_transaction,
)

@pytest.fixture
async def engine(async_engine_factory):
    async for eng in async_engine_factory("sqlite+aiosqlite:///:memory:"):
        yield eng

@pytest.fixture
async def session(async_session_factory, engine):
    async for sess in async_session_factory(engine):
        yield sess

async def test_with_session(session):
    # Session automatically has greenlet context
    result = await session.execute(text("SELECT 1"))
    assert result.scalar() == 1
```

### Transaction Management

Automatic transaction rollback for clean test isolation:

```python
from pytest_green_light.fixtures import async_db_transaction

async def test_with_rollback(session):
    # All changes automatically rolled back after test
    async with async_db_transaction(session):
        obj = MyModel(name="test")
        session.add(obj)
        await session.commit()
        # Changes are visible during the transaction
        result = await session.get(MyModel, obj.id)
        assert result is not None
    
    # After transaction, changes are rolled back
    result = await session.get(MyModel, obj.id)
    assert result is None  # Rolled back
```

### Configuration Options

The plugin works automatically with no configuration needed! It automatically:
- Detects async test functions
- Establishes greenlet context before tests run
- Works with any async testing plugin (pytest-asyncio, alt-pytest-asyncio, etc.)

You can also customize behavior with command-line options:

```bash
# Disable automatic greenlet context establishment
pytest --green-light-no-autouse

# Enable debug logging for greenlet context
pytest --green-light-debug
```

## How It Works

The plugin uses pytest hooks to:
1. Detect when async tests are about to run
2. Call SQLAlchemy's `greenlet_spawn` to establish the greenlet context
3. Ensure the context is available throughout the test execution

## Requirements

- Python 3.8+
- pytest 7.0+
- SQLAlchemy 2.0+
- greenlet 2.0+

## Features

- ✅ **Automatic greenlet context establishment** - No configuration needed
- ✅ **Helper fixtures** - Easy engine and session creation
- ✅ **Transaction management** - Automatic rollback for test isolation
- ✅ **Full test coverage** - 100% code coverage
- ✅ **Multiple database support** - SQLite, PostgreSQL, MySQL
- ✅ **Enhanced error messages** - Helpful diagnostics when issues occur
- ✅ **Python 3.8+ support** - Works with modern Python versions

## Examples

See the [examples/](examples/) directory for integration examples with FastAPI and other frameworks.

## Issues & Support

If you encounter any issues or have questions, please file an issue on [GitHub](https://github.com/eddiethedean/pytest-green-light/issues).

## Contributing

Contributions welcome! This plugin was created to solve a real-world problem with testing async SQLAlchemy code. 

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Odos Matthews**

- GitHub: [@eddiethedean](https://github.com/eddiethedean)
- Repository: [pytest-green-light](https://github.com/eddiethedean/pytest-green-light)

---

Made with ❤️ for the Python async testing community

