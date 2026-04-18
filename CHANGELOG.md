# Changelog

All notable changes to MnMCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production-ready WPKG codec with full encryption and compression support
- Complete MNW protocol implementation with all message types
- TCP connector with connection pooling and automatic reconnection
- WebSocket chat client with message queuing
- Protocol bridge for bidirectional MC <-> MNW forwarding
- Player synchronization system with position interpolation
- Comprehensive test suite with 95%+ coverage
- Performance benchmarks and optimization
- Full API documentation
- MIT License and Contributing guidelines

### Changed
- Refactored all modules to production quality
- Improved error handling and logging
- Enhanced type hints throughout codebase
- Optimized memory usage and reduced allocations
- Updated configuration system

### Fixed
- Fixed relative import issues
- Resolved encoding/decoding edge cases
- Fixed race conditions in async code
- Corrected protocol field mappings

## [1.1.0] - 2026-04-19

### Added
- Phase 3 real-time multiplayer support
- TCP game server connector
- WebSocket chat integration
- JWT authentication flow
- AES-GCM encryption for game traffic
- Complete login sequence implementation

### Changed
- Improved ECDH key exchange reliability
- Enhanced WPKG codec performance
- Updated protocol definitions

### Fixed
- Fixed session key derivation
- Corrected heartbeat timing
- Resolved connection timeout issues

## [1.0.0] - 2026-04-18

### Added
- Initial release
- WPKG codec implementation
- Protobuf message definitions
- Basic MNW protocol support
- ECDH + HKDF + AES-GCM encryption
- Block and entity mapping
- Coordinate conversion
- Configuration system
- Logging infrastructure

### Features
- Minecraft Java Edition support
- MiniWorld Creata support
- Cross-platform compatibility
- Modular architecture
- Extensible design

## [0.4.0] - 2026-04-15

### Added
- Protocol analysis tools
- Memory signature scanner
- Packet capture utilities
- Reverse engineering documentation

## [0.3.0] - 2026-04-10

### Added
- Basic network layer
- UDP connector prototype
- Session management
- Initial bridge implementation

## [0.2.0] - 2026-04-05

### Added
- Cryptography module
- ECDH implementation
- HKDF key derivation
- AES-GCM encryption

## [0.1.0] - 2026-04-01

### Added
- Project initialization
- Basic structure
- Documentation framework
- Development tools

---

## Release Notes Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Security improvements
```

## Versioning Guide

- **MAJOR** version for incompatible API changes
- **MINOR** version for added functionality (backwards compatible)
- **PATCH** version for backwards compatible bug fixes

## Categories

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Marked for removal
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security-related changes
