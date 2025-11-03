# Alternative Approaches and Workarounds

While we work on solving the greenlet context issue, here are alternative approaches developers can use:

## Current Workarounds

### 1. Test Outside Pytest

Use `asyncio.run()` directly for async SQLAlchemy testing:

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test_database():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        # Your test code here
        pass
    await engine.dispose()

# Run the test
asyncio.run(test_database())
```

**Pros**: Works reliably  
**Cons**: Doesn't integrate with pytest's test discovery, fixtures, or reporting

### 2. Use Sync SQLAlchemy for Tests

Use regular (non-async) SQLAlchemy engines for testing:

```python
from sqlalchemy import create_engine

@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")
```

**Pros**: No greenlet issues, simpler  
**Cons**: Doesn't test async code paths

### 3. Mock Async Operations

Mock SQLAlchemy async operations in tests:

```python
@pytest.fixture
def mock_async_engine():
    # Mock implementation
    pass
```

**Pros**: Fast, no database needed  
**Cons**: Doesn't test real async behavior

### 4. Use pytest-async-sqlalchemy (If It Works)

Try `pytest-async-sqlalchemy` - it may work in some configurations:

```bash
pip install pytest-async-sqlalchemy
```

**Pros**: Designed for this purpose  
**Cons**: May have the same greenlet issues we're experiencing

## What We're Trying to Solve

Our plugin aims to make this work seamlessly:

```python
# This is what we want to enable:
async def test_async_engine(engine):
    # No greenlet errors!
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
```

## Why These Workarounds Aren't Ideal

- **Outside pytest**: Loses pytest integration
- **Sync engines**: Doesn't test async code
- **Mocking**: Doesn't test real behavior
- **Other plugins**: May have the same issues

That's why we're building a solution that makes async SQLAlchemy testing in pytest "just work"!

