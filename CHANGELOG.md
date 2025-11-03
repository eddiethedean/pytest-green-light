# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2024-12-XX

### Fixed
- **Greenlet Context Persistence**: Fixed critical issue where greenlet context established in fixtures didn't persist to the async context where SQLAlchemy operations actually execute
  - Implemented `pytest_pyfunc_call` hook to wrap async test functions
  - Greenlet context is now established in the exact same async context where tests run
  - Ensures context is available when SQLAlchemy async engines make connections
  - Fixes `MissingGreenlet` errors that occurred even when the plugin was installed

### Changed
- Switched from `pytest_runtest_call` to `pytest_pyfunc_call` hook for better control over test function execution
- Updated internal implementation to wrap async test functions directly rather than relying solely on fixtures
- Changed status from Alpha to Beta as the plugin is now more stable and reliable

### Added
- Test cases specifically verifying the greenlet context persistence fix
- Enhanced documentation explaining how the hook-based approach works

## [0.1.0] - 2024-11-03

### Added
- Initial alpha release
- Automatic greenlet context establishment for SQLAlchemy async engines via auto-use fixture
- Plugin entry point registration
- Support for Python 3.8+
- Integration with pytest-asyncio
- Basic test suite with 100% coverage

[Unreleased]: https://github.com/eddiethedean/pytest-green-light/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/eddiethedean/pytest-green-light/releases/tag/v0.1.0

