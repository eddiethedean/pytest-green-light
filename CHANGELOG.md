# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2024-11-03

### Added
- **AsyncSession Fixtures**: `async_session_factory()` and `create_async_session_fixture()` helpers for easy session management
- **Transaction Management**: `async_db_transaction()` context manager and `async_transaction_fixture()` for automatic rollback and test isolation
  - Support for nested transactions (savepoints)
  - Configurable rollback behavior
- **Configuration Options**: Command-line flags for plugin customization
  - `--green-light-autouse` / `--green-light-no-autouse`: Control automatic greenlet context establishment
  - `--green-light-debug`: Enable debug logging for greenlet context establishment
- **Improved Error Messages**: Enhanced diagnostics when `MissingGreenlet` errors occur
  - Automatic detection and reporting of MissingGreenlet errors
  - Environment diagnostics (SQLAlchemy version, greenlet version, etc.)
  - Troubleshooting steps and suggestions
- **Enhanced Documentation**: Updated README with examples for all new features

### Changed
- Improved test coverage (93% overall)
- Enhanced plugin architecture for better extensibility

### Fixed
- Better handling of edge cases in greenlet context establishment
- Improved compatibility with different SQLAlchemy versions

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

