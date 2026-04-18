# Contributing to MnMCP

Thank you for your interest in contributing to MnMCP (Minecraft and MiniWorld Creata CrossPlay)! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Prioritize user safety and privacy

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include:

- **Use a clear descriptive title**
- **Describe the exact steps to reproduce**
- **Provide specific examples**
- **Describe the behavior you observed**
- **Explain which behavior you expected**
- **Include system information** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear descriptive title**
- **Provide a step-by-step description**
- **Provide specific examples**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- virtualenv (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/BlockConnect-MnMCP.git
cd BlockConnect-MnMCP

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_wpkg.py
```

### Code Style

We follow PEP 8 style guide. Please ensure your code:

- Passes `flake8` linting
- Is formatted with `black`
- Has type hints where appropriate
- Includes docstrings for public APIs

```bash
# Check code style
flake8 src

# Format code
black src

# Check types
mypy src
```

## Project Structure

```
BlockConnect-MnMCP/
├── src/                    # Python source code
│   ├── protocol/          # Protocol implementations
│   ├── crypto/            # Cryptography
│   ├── network/           # Network layer
│   ├── mapping/           # Data mapping
│   └── bridge.py          # Main bridge
├── mnmcp-core/            # Core library
│   └── src/mnmcp/
├── tests/                 # Test files
├── docs/                  # Documentation
└── tools/                 # Utility tools
```

## Coding Guidelines

### Python Code

- Use type hints
- Write docstrings in Google style
- Keep functions focused and small
- Use meaningful variable names
- Add comments for complex logic

Example:
```python
def process_packet(packet: MNWPacket) -> Optional[bytes]:
    """
    Process an MNW packet and return encoded data.
    
    Args:
        packet: The MNW packet to process
        
    Returns:
        Encoded bytes or None if processing failed
        
    Raises:
        ValueError: If packet format is invalid
    """
    if not packet.data:
        return None
    
    # Process logic here
    return packet.encode()
```

### Documentation

- Update README.md if needed
- Add docstrings to new functions
- Update API documentation
- Include examples for new features

### Testing

- Write unit tests for new functions
- Ensure tests cover edge cases
- Maintain test coverage above 80%
- Use pytest fixtures for setup

Example:
```python
def test_wpkg_encode_decode():
    """Test WPKG encoding and decoding."""
    codec = WPKGCodec()
    data = b"Hello, World!"
    
    encoded = codec.encode(data)
    decoded = codec.decode(encoded)
    
    assert decoded == data
```

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

Example:
```
Add WPKG codec support for LZ4 compression

- Implement LZ4 compression algorithm
- Add compression level configuration
- Update tests for new compression type

Fixes #123
```

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create a git tag
4. Push to GitHub
5. Create a GitHub release

## Security

- Never commit secrets or credentials
- Report security issues privately
- Follow secure coding practices
- Keep dependencies updated

## Questions?

- Check existing documentation
- Search closed issues
- Ask in discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to MnMCP!
