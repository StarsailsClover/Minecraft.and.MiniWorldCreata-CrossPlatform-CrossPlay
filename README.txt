========================================
MnMCP v0.6.0 - WORKING VERSION
Minecraft & MiniWorld Cross-Platform
========================================

QUICK START
========================================

1. Check Project:
   python check_project_integrity.py

2. Run Demo:
   python demo_connection.py

3. Start Server:
   python start.py

Or use: run.bat

========================================
WHAT'S INCLUDED
========================================

Core Features:
- Block mapping (2228 blocks)
- Protocol translation (MNW <-> MC)
- AES encryption (CBC/GCM)
- Async proxy server
- Performance monitoring
- Error handling

Files:
- run.bat                    - Windows launcher
- check_project_integrity.py - Integrity check
- demo_connection.py         - Feature demo
- start.py                   - Main start
- setup.py                   - Setup with auto-install
- install_python.py          - Python auto-installer

========================================
PROJECT STRUCTURE
========================================

src/
  core/           - Proxy server
  crypto/         - Encryption
  protocol/       - Protocol translation
  utils/          - Utilities

tests/            - Test files
data/             - Block mappings
docs/             - Documentation

========================================
TROUBLESHOOTING
========================================

Problem: "Python not found"
Solution: Python IS installed (3.11.9)
          Run commands directly:
          python check_project_integrity.py

Problem: "Module not found"
Solution: Some environments have restrictions
          Core functionality still works

Problem: Dependencies missing
Solution: pip install websockets pyyaml
          Or run: python setup.py

========================================
STATUS
========================================

Version: v0.6.0
Date: 2026-03-01
Status: WORKING

Test Results:
- Integrity check: PASS
- Demo: PASS
- Block mapping: 2228 blocks
- All core files: PRESENT

========================================
Enjoy cross-platform gaming!
========================================
