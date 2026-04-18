"""
MnMCP Setup Script

Minecraft and MiniWorld Creata CrossPlay Protocol Bridge
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version from __init__.py
version = "1.1.0"

setup(
    name="mnmcp",
    version=version,
    author="MnMCP Contributors",
    author_email="mnmcp@example.com",
    description="Minecraft and MiniWorld Creata CrossPlay Protocol Bridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/BlockConnect-MnMCP",
    packages=find_packages(where="src") + find_packages(where="mnmcp-core/src"),
    package_dir={
        "": "src",
        "mnmcp": "mnmcp-core/src/mnmcp",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "performance": [
            "lz4>=4.3.0",
            "orjson>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mnmcp=mnmcp.cli:main",
            "mnmcp-server=mnmcp.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mnmcp": ["data/*.json", "config/*.yaml"],
    },
    zip_safe=False,
    keywords="minecraft miniworld crossplay protocol bridge multiplayer",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/BlockConnect-MnMCP/issues",
        "Source": "https://github.com/yourusername/BlockConnect-MnMCP",
        "Documentation": "https://mnmcp.readthedocs.io/",
    },
)
