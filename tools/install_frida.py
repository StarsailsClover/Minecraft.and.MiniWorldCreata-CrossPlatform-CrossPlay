import sys
import subprocess

# Set up Python path
tools_path = r'C:\Users\Sails\Documents\Coding\Minecraft.and.MiniWorldCreata-CrossPlatform-CrossPlay\tools\python_libs'
sys.path.insert(0, tools_path)

# Install frida using pip
subprocess.run([
    sys.executable, 
    '-m', 'pip', 
    'install', 
    '--target=' + tools_path,
    'frida-tools'
])
