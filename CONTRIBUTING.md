# Contributing to pytest-green-light

Thank you for your interest in contributing! This project is solving a real-world problem that affects many developers testing async SQLAlchemy code.

## Current Challenge

The core issue is establishing SQLAlchemy's greenlet context in pytest fixtures. The `MissingGreenlet` error occurs because:

1. SQLAlchemy async engines require greenlet context during connection creation
2. `greenlet_spawn` is a coroutine that must be awaited
3. The context must be established in the same async context where operations will run
4. Pytest fixtures don't automatically provide this context the way `asyncio.run()` does

## How to Help

### Option 1: Research and Experiment

1. **Study SQLAlchemy's async internals**:
   - Read `sqlalchemy/util/_concurrency_py3k.py`
   - Understand how `greenlet_spawn` works
   - Trace when greenlet context is actually needed

2. **Experiment with different approaches**:
   - Try establishing context at different points in the test lifecycle
   - Experiment with wrapping `create_async_engine`
   - Test connection pooling hooks

3. **Document your findings** in issues or discussions

### Option 2: Implement a Solution

If you find a working approach:

1. **Create a test that demonstrates the fix**:
   ```python
   async def test_async_engine_works():
       engine = create_async_engine("sqlite+aiosqlite:///:memory:")
       # This should NOT raise MissingGreenlet
       async with engine.begin() as conn:
           result = await conn.execute(text("SELECT 1"))
           assert result.scalar() == 1
   ```

2. **Update the plugin code** to implement your solution

3. **Ensure tests pass**:
   ```bash
   pytest tests/ -v
   ```

4. **Test with real projects**:
   - Try it with `pandalchemy` async tests
   - Test with other SQLAlchemy async projects

### Option 3: Document Alternatives

If you find alternative approaches or workarounds:

1. Document them in `ALTERNATIVES.md`
2. Update the README with links
3. Share your experiences

## Development Setup

```bash
# Clone the repository
cd pytest-green-light

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with pandalchemy tests
cd ../pandalchemy
pip install -e ../pytest-green-light
pytest tests/test_async.py -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

## Questions?

- Open an issue for discussion
- Check existing issues for known problems
- Review [DEVELOPMENT.md](DEVELOPMENT.md) for technical details

## Recognition

Contributors who help solve the greenlet context issue will be prominently credited in the README and release notes!

