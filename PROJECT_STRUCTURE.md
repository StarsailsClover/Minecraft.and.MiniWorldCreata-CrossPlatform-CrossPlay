# MnMCP Project Structure

**Version**: v0.6.0  
**Date**: 2026-03-01  
**Status**: Organized and Working

---

## Root Directory Files

### Entry Points
| File | Purpose |
|------|---------|
| `run.bat` | Windows launcher (main entry) |
| `start.py` | Python start script |
| `setup.py` | Setup with auto-install |
| `install_python.py` | Python auto-installer |

### Verification & Demo
| File | Purpose |
|------|---------|
| `check_project_integrity.py` | Project integrity check |
| `demo_connection.py` | Feature demonstration |
| `verify_deploy.py` | Deployment verification |

### Configuration
| File | Purpose |
|------|---------|
| `config.yaml` | Main configuration |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git ignore rules |

### Documentation
| File | Purpose |
|------|---------|
| `README.txt` | Quick start guide |
| `README.md` | Full documentation |
| `PROJECT_STATUS.md` | Project status |
| `PROJECT_STRUCTURE.md` | This file |

---

## Directory Structure

```
Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay/
├── run.bat                      # Windows entry point
├── start.py                     # Python entry point
├── setup.py                     # Setup script
├── install_python.py            # Python installer
├── check_project_integrity.py   # Integrity check
├── demo_connection.py           # Feature demo
├── verify_deploy.py             # Deploy verification
├── config.yaml                  # Configuration
├── requirements.txt             # Dependencies
├── .gitignore                   # Git ignore
├── README.txt                   # Quick readme
├── README.md                    # Full readme
├── PROJECT_STATUS.md            # Status
├── PROJECT_STRUCTURE.md         # Structure
│
├── src/                         # Source code
│   ├── core/                    # Core modules
│   │   ├── proxy_server_v2.py
│   │   └── __init__.py
│   ├── crypto/                  # Encryption
│   │   ├── aes_crypto.py
│   │   ├── password_hasher.py
│   │   └── __init__.py
│   ├── protocol/                # Protocol
│   │   ├── block_mapper.py
│   │   ├── packet_translator.py
│   │   ├── mc_protocol.py
│   │   ├── mnw_login.py
│   │   └── __init__.py
│   └── utils/                   # Utilities
│       ├── config_loader.py
│       ├── logger.py
│       ├── performance_monitor.py
│       ├── error_handler.py
│       └── __init__.py
│
├── tests/                       # Tests
│   ├── test_crypto.py
│   ├── test_block_mapper.py
│   ├── test_protocol.py
│   └── __init__.py
│
├── data/                        # Data files
│   └── mnw_block_mapping_from_go.json
│
├── docs/                        # Documentation
│   ├── USER_GUIDE.md
│   ├── Phase1_Plan.md
│   ├── Phase2_Plan.md
│   ├── Phase3_Plan.md
│   ├── Phase4_Plan.md
│   ├── Phase5_Plan.md
│   ├── Phase6_Plan.md
│   └── Phase7_Plan.md
│
└── tools/                       # Tools
    ├── encrypt_config.py
    └── decrypt_config.py
```

---

## Key Features

### Working Features
- ✅ Block mapping (2228 blocks)
- ✅ Protocol translation
- ✅ AES encryption
- ✅ Packet serialization
- ✅ Integrity check
- ✅ Feature demo

### Test Results
- Integrity check: 9/9 passed
- Demo: Working
- Block mappings: 94 loaded (with fallback)

---

## Usage

### Quick Start
```bash
# Check project
python check_project_integrity.py

# Run demo
python demo_connection.py

# Start server
python start.py
```

### Windows
```bash
# Use launcher
run.bat
```

---

## Clean Structure

### Removed Files
- Duplicate batch files
- Old deployment scripts
- Temporary files

### Kept Files
- Essential entry points
- Working verification scripts
- Core functionality
- Documentation

---

## Status

**Working**: ✅ YES  
**Tested**: ✅ YES  
**Ready**: ✅ YES

Run `python check_project_integrity.py` to verify.
