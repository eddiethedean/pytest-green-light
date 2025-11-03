# Greenlet Context Persistence Issue

> ✅ **RESOLVED** - This issue has been fixed by implementing the `pytest_runtest_call` hook approach (Option 1). The hook establishes greenlet context in the exact same async context where tests run, ensuring context persistence.

## Problem Statement

The `pytest-green-light` plugin's autouse async fixture `ensure_greenlet_context` establishes greenlet context, but this context does not persist to the async context where SQLAlchemy async engines actually make connections.

## Symptoms

When using `pytest-green-light` with SQLAlchemy async engines (especially `aiosqlite`), tests still fail with:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
```

This occurs even though:
- The plugin is installed and loaded
- The `ensure_greenlet_context` fixture runs (visible in `--setup-show`)
- Greenlet context establishment works when called manually in the same async context

## Root Cause Analysis

SQLAlchemy's async engines require greenlet context to be established in the **exact same async context** where connections are made. The issue is:

1. The `ensure_greenlet_context` fixture runs in its own async context (fixture lifecycle)
2. When the test function executes `async with engine.begin()`, it may run in a different async context
3. Greenlet context established in the fixture's context doesn't carry over to the test's async context

## Evidence

### Working Case (Manual Test)
```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.util._concurrency_py3k import greenlet_spawn

async def test():
    def _noop():
        pass
    await greenlet_spawn(_noop)  # Establish context
    
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:  # ✅ Works!
        result = await conn.execute(text('SELECT 1'))
        print(result.scalar())

asyncio.run(test())
```

### Failing Case (Pytest)
```python
@pytest.fixture(scope="function", autouse=True)
async def ensure_greenlet_context(request):
    await greenlet_spawn(_noop)  # Establish context
    yield

async def test_my_code():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:  # ❌ MissingGreenlet!
        result = await conn.execute(text('SELECT 1'))
```

## Why Current Implementation Fails

The current `ensure_greenlet_context` fixture:
- Runs before the test function
- Establishes greenlet context in the fixture's async context
- Yields control back to pytest
- Test function runs in a potentially different async context
- Greenlet context from fixture is not available

## Proposed Solutions

### Option 1: Hook into Test Execution (Recommended)
Use `pytest_runtest_call` hook to establish greenlet context right before the test function executes:

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    # Establish greenlet context in the same async context as the test
    if asyncio.iscoroutinefunction(item.function):
        # We need to wrap the test execution
        yield
    else:
        yield
```

### Option 2: Wrap Test Execution
Create a wrapper that establishes greenlet context around test execution:

```python
@pytest.fixture(autouse=True)
async def ensure_greenlet_context_during_test(request):
    # Establish context before test
    await greenlet_spawn(_noop)
    
    # Run test wrapped in greenlet context
    yield
    
    # Context persists during test execution
```

### Option 3: Use pytest-asyncio Integration
Integrate with pytest-asyncio's event loop management to establish context at the event loop level:

```python
@pytest.fixture(scope="function")
async def event_loop_with_greenlet():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Establish greenlet context in this event loop
    await greenlet_spawn(_noop)
    
    yield loop
    loop.close()
```

### Option 4: Context Manager Approach
Provide a context manager that tests can use:

```python
@pytest.fixture
async def greenlet_context():
    async with ensure_greenlet_context():
        yield
```

## Recommended Approach

**Option 1** (hook into test execution) is recommended because:
- It establishes context in the exact async context where the test runs
- It works with pytest-asyncio's event loop management
- It doesn't require changes to test code
- It's transparent to users

## Resolution

✅ **IMPLEMENTED** - The fix has been implemented using Option 1 (hook into test execution).

### Implementation Details

The `pytest_runtest_call` hook has been implemented in `src/pytest_green_light/plugin.py`. The hook:

1. Detects async test functions using `inspect.iscoroutinefunction()`
2. Wraps async test functions to establish greenlet context before execution
3. Ensures context is established in the exact same async context where the test runs
4. Works seamlessly with pytest-asyncio's event loop management

### Code Changes

The hook wraps async test functions like this:

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item):
    if is_async and greenlet_spawn is not None:
        original_function = item.function
        
        async def wrapped_test_function(*args, **kwargs):
            # Establish greenlet context in the same async context as the test
            await _establish_greenlet_context_async(debug=debug)
            # Run the original test function
            return await original_function(*args, **kwargs)
        
        item.function = wrapped_test_function
    
    yield  # Execute the test
```

### Verification

Test cases have been added in `tests/test_greenlet_context_fix.py` to verify:
- Async engines work with the hook approach
- Context persists across multiple connection operations
- Direct engine creation in tests works without fixtures
- Compatibility with existing fixture patterns

The fix ensures that greenlet context is established in the exact async context where SQLAlchemy operations occur, solving the context persistence issue.

## Test Case to Verify Fix

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

@pytest.mark.asyncio
async def test_async_engine_works():
    """This test should pass once the fix is implemented."""
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    
    # This should work without MissingGreenlet error
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT 1'))
        assert result.scalar() == 1
    
    await engine.dispose()
```

## Previous Workaround (No Longer Needed)

~~Until this is fixed, users must establish greenlet context manually in their async operations:~~

**Note:** This workaround is no longer needed as the issue has been resolved. The plugin now automatically establishes greenlet context in the correct async context.

```python
async def my_async_operation():
    # Establish greenlet context right before async operations
    from sqlalchemy.util._concurrency_py3k import greenlet_spawn
    await greenlet_spawn(lambda: None)
    
    # Now async operations work
    async with engine.begin() as conn:
        # ...
```

This is not ideal because it requires changes to production code.

## Related Issues

- SQLAlchemy async documentation mentions greenlet context requirements
- pytest-asyncio doesn't automatically establish greenlet context
- This affects all SQLAlchemy async drivers (aiosqlite, asyncpg, aiomysql)

## References

- SQLAlchemy async documentation: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Greenlet documentation: https://greenlet.readthedocs.io/
- pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio

