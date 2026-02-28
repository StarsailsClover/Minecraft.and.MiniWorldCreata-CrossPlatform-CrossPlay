==========================================
MnMCP - Minecraft & MiniWorld Cross-Platform
==========================================

Version: v0.6.0
Date: 2026-02-28

------------------------------------------
QUICK START
------------------------------------------

1. Double click: QUICK_START.bat
   - This will check dependencies
   - Show menu to start server or demo

2. Or double click: DEPLOY_AND_START.bat
   - Full deployment with all checks
   - Opens user guide automatically

3. Or manually:
   - Install Python 3.11+ from python.org
   - Run: pip install websockets pyyaml
   - Run: python start.py

------------------------------------------
HOW TO CONNECT
------------------------------------------

1. Start Proxy Server:
   - Run QUICK_START.bat
   - Select option 1
   - Server will start on ports 8080 and 19132

2. Start Minecraft:
   - Open Minecraft Launcher
   - Select version 1.20.6
   - Multiplayer -> Add Server
   - Address: 127.0.0.1:19132
   - Join Server

3. Start MiniWorld:
   - Open MiniWorld
   - Start Game -> Multiplayer Hall
   - Create Room
   - Advanced Settings -> Server: 127.0.0.1:8080
   - Create

4. Enjoy cross-platform multiplayer!

------------------------------------------
FILES
------------------------------------------

QUICK_START.bat       - Quick start menu
DEPLOY_AND_START.bat  - Full deployment
start.bat            - Simple start
start.py             - Python start script

docs\USER_GUIDE.md   - Full user guide
PROJECT_STATUS.md    - Project status

tests\              - Test files
src\                 - Source code
data\                - Block mappings

------------------------------------------
TROUBLESHOOTING
------------------------------------------

Problem: Python not found
Solution: Install Python 3.11+ from https://python.org

Problem: Dependencies missing
Solution: Run: pip install websockets pyyaml

Problem: Port already in use
Solution: Edit config.yaml, change port numbers

------------------------------------------
HELP
------------------------------------------

GitHub: https://github.com/starsailsclover
Website: https://starsailsclover.github.io/MnMCP-Introducing-Website/
QQ Group: 1084172731

------------------------------------------
Enjoy cross-platform gaming!
==========================================
