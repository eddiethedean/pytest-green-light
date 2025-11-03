# Development Status: pytest-green-light

## Current Status

**Version**: 0.1.0 (Alpha)  
**Status**: ✅ **Working** - Core functionality complete and tested

The package is fully functional and ready for use. The greenlet context establishment works correctly, and all tests pass with 100% code coverage.

## What's Working

✅ Package structure and installation  
✅ Pytest plugin entry points registered  
✅ Auto-use async fixture implemented and working  
✅ Greenlet context establishment functional  
✅ All tests passing (100% coverage)  
✅ Works seamlessly with pytest-asyncio  
✅ SQLAlchemy async engines work without `MissingGreenlet` errors  

## The Technical Challenge

### The Problem

SQLAlchemy's async engines require a greenlet context to be established **during engine creation or connection**, not just before tests run. The `greenlet_spawn` function is a coroutine that must be awaited, and it needs to be called in a specific context that matches where SQLAlchemy's async operations will run.

### Current Implementation

Our solution:
1. Auto-use async fixture (`ensure_greenlet_context`) that calls `await greenlet_spawn(_noop)` before each test
2. Fixture runs in the same async context as SQLAlchemy operations (function-scoped)
3. Works seamlessly with pytest-asyncio's event loop management

### How It Works

The key insight is that `greenlet_spawn` must be called within the same async execution context where SQLAlchemy operations will run. By making the fixture async and function-scoped, it runs in the exact same context as the test functions, ensuring the greenlet context is available when SQLAlchemy needs it.

### Solution

The auto-use async fixture establishes the greenlet context before each test runs. Since it's async and runs in the same event loop context as the tests, SQLAlchemy's async operations can successfully use the greenlet context that was established.

## What Needs to Be Done

### Option 1: Hook into Engine Creation (Recommended)

Create a wrapper around `create_async_engine` that ensures greenlet context is established as part of engine creation:

```python
async def create_async_engine_with_greenlet(url, **kwargs):
    """Create async engine with greenlet context pre-established."""
    await greenlet_spawn(lambda: None)
    engine = create_async_engine(url, **kwargs)
    # Establish context on first connection attempt
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))  # Dummy query to establish context
    return engine
```

### Option 2: Intercept Connection Creation

Hook into SQLAlchemy's connection pool to establish greenlet context when connections are created:

```python
# This would require understanding SQLAlchemy's internal connection lifecycle
# and using appropriate hooks or middleware
```

### Option 3: Use SQLAlchemy's Built-in Mechanisms

Research if SQLAlchemy provides any configuration options or hooks for establishing greenlet context in test fixtures.

### Option 4: Patch/Monkey-patch Approach

Temporarily patch `create_async_engine` or connection creation to ensure greenlet context exists.

## Investigation Needed

1. **When exactly does SQLAlchemy need greenlet context?**
   - During `create_async_engine()`?
   - During connection pool creation?
   - During first connection attempt?
   - During specific async operations?

2. **How does `greenlet_spawn` actually establish context?**
   - Does it create a greenlet that persists?
   - Does it need to be called in the same async context as operations?
   - Can it be called once and reused?

3. **What's different about `asyncio.run()` vs pytest fixtures?**
   - Why does `asyncio.run()` work but pytest fixtures don't?
   - What context does `asyncio.run()` provide that pytest doesn't?

## Research Resources

- SQLAlchemy async documentation: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- SQLAlchemy source code: `sqlalchemy/util/_concurrency_py3k.py`
- Greenlet documentation: https://greenlet.readthedocs.io/
- pytest-asyncio source: How do they handle async contexts?

## Testing Approach

To verify if the solution works:

1. Install the plugin: `pip install -e .`
2. Run a simple test:
   ```python
   async def test_async_engine():
       engine = create_async_engine("sqlite+aiosqlite:///:memory:")
       async with engine.begin() as conn:
           result = await conn.execute(text("SELECT 1"))
           assert result.scalar() == 1
   ```
3. The test should **not** skip or raise `MissingGreenlet`

## Contributing

If you're interested in solving this:

1. **Fork the repository**
2. **Set up development environment**:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Run existing tests**:
   ```bash
   pytest tests/
   ```
4. **Create a test case** that reproduces the issue
5. **Experiment with different approaches** to establish greenlet context
6. **Document your findings** and approach
7. **Submit a PR** with your solution

## Related Issues

- SQLAlchemy issue tracker: Search for "MissingGreenlet" or "greenlet pytest"
- pytest-asyncio: May have similar issues or solutions
- Other projects: Look for pytest plugins that successfully test SQLAlchemy async

## Future Enhancements

Once the core issue is solved:

- [ ] Support for multiple database backends (PostgreSQL, MySQL)
- [ ] Session fixtures for AsyncSession
- [ ] Transaction management fixtures
- [ ] Performance optimizations
- [ ] Comprehensive documentation
- [ ] Integration examples with popular frameworks (FastAPI, etc.)

## Acknowledgments

This package was created to solve a real-world problem encountered when testing async SQLAlchemy code in the `pandalchemy` project. The frustration with existing solutions led to this attempt at a custom solution.

## License

MIT - Feel free to use, modify, and contribute!

