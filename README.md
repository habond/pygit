# PyGit 🚀

[![Tests](https://github.com/habond/pygit/actions/workflows/test.yml/badge.svg)](https://github.com/habond/pygit/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/habond/pygit/branch/main/graph/badge.svg)](https://codecov.io/gh/habond/pygit)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A basic Git implementation in Python built for educational purposes. This project demonstrates the core concepts and data structures that make Git work.

## Features ✨

- **Repository initialization** (`init`)
- **File staging** (`add`) 
- **Status checking** (`status`)
- **Creating commits** (`commit`)
- **Object storage** (blobs, trees, commits)
- **Content-addressable storage** with SHA-1 hashing
- **Branch management** (HEAD tracking)

## Installation & Usage

### Requirements
- Python 3.9+
- Dependencies listed in `requirements.txt`

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd pygit

# Run PyGit commands
python3 src/main.py init                    # Initialize repository
echo "Hello World" > test.txt              # Create a file
python3 src/main.py add test.txt           # Stage the file
python3 src/main.py status                 # Check status
python3 src/main.py commit -m "First!"     # Create commit
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init [path]` | Initialize new repository | `python3 src/main.py init` |
| `add <file>` | Stage file for commit | `python3 src/main.py add file.txt` |
| `status` | Show working tree status | `python3 src/main.py status` |
| `commit [-m <message>]` | Create commit from staged files | `python3 src/main.py commit -m "Add feature"` |
| `hash-object [-w] <file>` | Hash file and optionally store | `python3 src/main.py hash-object -w file.txt` |
| `cat-file [-t\|-s] <sha1>` | Show object content/type/size | `python3 src/main.py cat-file abc123...` |
| `write-tree` | Create tree from working directory | `python3 src/main.py write-tree` |
| `ls-tree <sha1>` | List tree contents | `python3 src/main.py ls-tree abc123...` |
| `commit-tree <tree> [-m <msg>] [-p <parent>]` | Create commit object | `python3 src/main.py commit-tree abc123 -m "msg"` |

## Architecture 🏗️

### Project Structure
```
src/
├── main.py              # Entry point
└── pygit/               # Main package
    ├── __init__.py      # Package metadata
    ├── objects.py       # Git objects (blobs, trees, commits)
    ├── index.py         # Staging area management
    ├── repository.py    # Repository & branch operations
    ├── commands.py      # Command implementations
    └── cli.py           # CLI argument parsing

tests/                   # Comprehensive test suite
├── conftest.py         # Pytest fixtures
├── test_objects.py     # Object storage tests
├── test_index.py       # Staging area tests  
├── test_repository.py  # Repository tests
├── test_commands.py    # Command tests
└── test_integration.py # End-to-end tests
```

### Core Concepts

**Git Objects:**
- **Blobs**: Store file contents
- **Trees**: Store directory structure (like filesystem snapshots)  
- **Commits**: Store snapshots with metadata (author, message, parent)

**Storage:**
- Content-addressable storage using SHA-1 hashes
- Objects stored in `.pygit/objects/xx/xxxxx...` format
- Compression with zlib (just like real Git)

**Workflow:**
1. **Working Directory** → `add` → **Staging Area** → `commit` → **Repository**
2. Three-stage workflow identical to Git
3. HEAD tracks current branch, branches point to commits

## Development 🛠️

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type check
mypy src/

# Run tests
pytest

# All quality checks
black src/ tests/ && flake8 src/ tests/ && mypy src/ && pytest
```

### Testing
- **44 comprehensive tests** covering all functionality
- **Filesystem isolation** using temporary directories  
- **Unit tests** for individual modules
- **Integration tests** for complete workflows
- Run with `pytest -v` for verbose output

### Dependencies
```bash
# Install development dependencies
pip install -r requirements.txt

# Or use homebrew (recommended)
brew install mypy black flake8 pytest
```

## Learning Outcomes 📚

Building this project teaches:

1. **Git Internals**: How Git actually stores data
2. **Content-Addressable Storage**: Everything identified by hash
3. **Object Model**: Blobs → Trees → Commits hierarchy  
4. **Staging Area**: Three-stage workflow (working → staging → repo)
5. **Hash Functions**: SHA-1 for integrity and deduplication
6. **Compression**: Data storage optimization
7. **Branch Management**: Pointers and HEAD tracking

## Architecture Decisions

- **Modular Design**: Separated concerns into focused modules
- **Type Safety**: Full type hints + mypy checking  
- **Test Coverage**: Isolated tests with temporary directories
- **Code Quality**: Black formatting + flake8 linting
- **Python Packaging**: Proper package structure

## What's Missing (vs Real Git)

This is an educational implementation. Missing features include:
- Network operations (clone, push, pull)
- Advanced branching/merging
- Checkout functionality  
- Diff algorithms
- Packfiles and delta compression
- Hooks and configuration
- Advanced CLI features

## Contributing

This is a learning project! Feel free to:
- Add new commands
- Improve test coverage
- Optimize performance
- Add documentation

## License

Educational project - feel free to learn from and modify!

---

*Built as a learning exercise to understand Git internals* ⚡