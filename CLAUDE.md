# CLAUDE.md - Development Documentation

This document provides comprehensive information about the PyGit project for Claude Code and future development.

## Project Overview

PyGit is a basic Git implementation in Python built for educational purposes. It demonstrates core Git concepts including content-addressable storage, object models, and basic version control workflows.

**Repository**: https://github.com/habond/pygit  
**Language**: Python 3.9+  
**Architecture**: Modular Python package with comprehensive test coverage  

## Development Environment Setup

### Prerequisites
- Python 3.9 or higher
- pip (for installing dependencies)

### Installation
```bash
# Clone the repository
git clone https://github.com/habond/pygit.git
cd pygit

# Install development dependencies
pip install -r requirements.txt

# Run tests to verify setup
pytest tests/ -v

# Run linting and type checking
flake8 src/
mypy src/
```

### Running the Application
```bash
# Recommended: Use the wrapper script
./pygit <command> [args...]

# Example commands
./pygit init
./pygit add file.txt  
./pygit commit -m "message"
./pygit log
./pygit checkout <sha1>

# Alternative: Direct Python execution
PYTHONPATH=. python3 -m src.main <command> [args...]
```

## Project Structure

```
pygit/
├── src/                     # Main source code
│   ├── __init__.py         # Package metadata
│   ├── main.py             # Entry point
│   ├── cli.py              # Command-line interface
│   ├── commands.py         # High-level command implementations  
│   ├── objects.py          # Git object storage (blobs, trees, commits)
│   ├── index.py            # Staging area management
│   └── repository.py       # Repository initialization and management
│
├── tests/                   # Comprehensive test suite (47 tests)
│   ├── conftest.py         # Pytest fixtures for isolation
│   ├── test_objects.py     # Object storage tests
│   ├── test_index.py       # Staging area tests
│   ├── test_repository.py  # Repository tests  
│   ├── test_commands.py    # Command implementation tests
│   └── test_integration.py # End-to-end workflow tests
│
├── .github/workflows/      # CI/CD pipeline
│   └── test.yml           # GitHub Actions testing workflow
│
├── requirements.txt        # Python dependencies
├── pytest.ini            # Pytest configuration
├── mypy.ini              # MyPy type checking configuration
├── .flake8              # Flake8 linting configuration
├── pygit                 # Executable wrapper script for easy usage
├── LICENSE              # MIT license
├── README.md           # User documentation  
└── CLAUDE.md           # Development documentation (this file)
```

## Core Architecture

### 1. Object Storage (`src/objects.py`)
Implements Git's content-addressable storage system:

**Functions**:
- `hash_object(data, obj_type, write)` - Hash and optionally store objects
- `read_object(sha1)` - Retrieve objects by SHA-1 hash
- `create_tree_object(entries)` - Create tree objects from file lists
- `parse_tree_object(content)` - Parse tree object binary format
- `create_commit_object(tree_sha1, parent, message)` - Create commit objects

**Storage Location**: `.pygit/objects/XX/YYYYYYYY...` (first 2 chars as directory)
**Compression**: Uses zlib for storage efficiency
**Hashing**: SHA-1 for content addressing

### 2. Index/Staging Area (`src/index.py`)
Manages the staging area between working directory and repository:

**Functions**:
- `read_index()` - Read current staging area state
- `write_index(index)` - Persist staging area to disk
- `add_to_index(filepath)` - Stage file for commit
- `create_tree_from_index(current_tree_entries)` - Create tree from staged files

**Storage**: `.pygit/index` (tab-separated format: `<sha1>\t<filepath>`)
**Behavior**: Merges staged files with existing tree entries

### 3. Repository Management (`src/repository.py`)  
Handles repository initialization and HEAD management:

**Functions**:
- `init_repository(path)` - Initialize new repository structure
- `get_current_commit()` - Get current HEAD commit SHA-1
- `update_branch(commit_sha1)` - Update current branch pointer
- `get_current_tree_entries()` - Get files from current commit's tree

**Storage**: 
- `.pygit/HEAD` - Points to current branch (e.g., "ref: refs/heads/main")
- `.pygit/refs/heads/main` - Branch pointer to latest commit

### 4. Command Layer (`src/commands.py`)
High-level command implementations:

**Commands**:
- `init` - Initialize repository
- `add` - Stage files
- `status` - Show working tree status  
- `commit` - Create commits from staged files
- `checkout` - Restore working directory from commits
- `log` - Display commit history with messages and metadata
- `hash-object`, `cat-file`, `write-tree`, `ls-tree`, `commit-tree` - Low-level operations

### 5. CLI Interface (`src/cli.py`)
Command-line argument parsing and dispatching:

- Handles all argument parsing
- Provides help text
- Dispatches to appropriate command functions
- Error handling and user feedback

## Key Features Implemented

### ✅ Core Git Workflow
- Repository initialization with `.pygit` directory
- File staging with SHA-1 content addressing
- Commit creation with tree and parent linking
- Working directory status checking
- Commit history navigation with checkout
- Commit history viewing with log display

### ✅ Object Model
- **Blobs**: File content storage
- **Trees**: Directory/file listings with modes and names
- **Commits**: Snapshots with tree, parent, and metadata
- Content-addressable storage with zlib compression

### ✅ Index/Staging
- Files staged independently of commits
- Index cleared after successful commits  
- Tree merging (staged files + existing files)

### ✅ Branch Management
- HEAD pointer management
- Branch reference tracking
- Parent commit linking for history

## Testing Strategy

### Test Coverage: 50 tests across 5 test files

1. **Unit Tests** (`test_objects.py`, `test_index.py`, `test_repository.py`)
   - Individual function testing
   - Edge case handling
   - Error condition testing

2. **Command Tests** (`test_commands.py`)  
   - All command implementations
   - CLI argument handling
   - Output verification

3. **Integration Tests** (`test_integration.py`)
   - End-to-end workflows
   - Multi-commit scenarios
   - File modification workflows

### Test Isolation
- Uses temporary directories via `pytest.fixture`
- Each test gets clean filesystem state
- No interference between test runs

### Continuous Integration
- GitHub Actions workflow on Python 3.9-3.12
- Runs linting (flake8), type checking (mypy), and tests (pytest)
- Code coverage reporting via Codecov

## Development Guidelines

### Code Quality Standards
- **Type Hints**: Full type annotations using `mypy`
- **Linting**: Code style enforced with `flake8` 
- **Formatting**: Consistent style with `black`
- **Testing**: Comprehensive test coverage required

### Adding New Features

1. **Design**: Consider Git compatibility and educational value
2. **Implementation**: 
   - Add to appropriate module (`objects.py`, `commands.py`, etc.)
   - Follow existing patterns and type annotations
   - Handle errors gracefully with user-friendly messages

3. **CLI Integration**:
   - Add command to `cli.py` with help text
   - Follow existing argument parsing patterns

4. **Testing**:
   - Add unit tests for core functionality
   - Add command tests for CLI behavior  
   - Add integration tests for workflows
   - Ensure all tests pass

5. **Documentation**: Update README.md and this CLAUDE.md

### Common Patterns

#### Error Handling
```python
try:
    # Operation that might fail
    result = some_operation()
except FileNotFoundError:
    print("Error: file not found")
    return
except Exception as e:
    print(f"Error: {e}")
    return
```

#### Object Storage Pattern
```python
# Store object
sha1 = hash_object(content, "blob", write=True)

# Read object  
obj_type, size, content = read_object(sha1)
```

#### Command Implementation Pattern
```python
def new_command(arg1: str, arg2: bool = False) -> None:
    """Command description for help text."""
    try:
        # Validate inputs
        if not validate_input(arg1):
            print("Error: invalid input")
            return
            
        # Perform operation
        result = do_operation(arg1, arg2)
        
        # Provide user feedback
        print(f"Success: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
```

## Known Limitations

1. **No Network Operations**: No remote repository support (push/pull/clone)
2. **No Branching**: Only main branch supported (HEAD management only)  
3. **No Merge**: No three-way merge capabilities
4. **Basic Checkout**: Only full working directory checkout (no partial)
5. **No .gitignore**: All files are considered for staging
6. **No Subdirectories**: Limited directory tree support in checkout

## Future Enhancement Ideas

### High Priority
- Branch creation and switching (`branch`, `switch`)
- `.pygitignore` file support  
- Improved directory handling in checkout
- Partial file checkout capabilities

### Medium Priority  
- Three-way merge support
- Conflict resolution
- Tag support
- Better diff visualization

### Low Priority
- Remote repository support
- Network operations (push/pull)
- Performance optimizations
- Advanced Git features (rebase, stash, etc.)

## Troubleshooting

### Common Issues

**ModuleNotFoundError**: 
- Ensure you're running from project root
- Use `PYTHONPATH=. python3 -m src.main` syntax
- Verify Python 3.9+ is being used

**Permission Errors**:
- Ensure write permissions in working directory
- `.pygit` directory must be writable

**Object Not Found**:
- Verify SHA-1 hashes are complete (40 characters)  
- Ensure repository is initialized
- Check that objects exist in `.pygit/objects/`

**Test Failures**:
- Run `pytest tests/ -v` for detailed output
- Check that dependencies are installed
- Verify Python version compatibility

### Debugging Tips

1. **Enable Verbose Output**: Add debug prints to command functions
2. **Inspect Repository State**: 
   - Check `.pygit/HEAD` contents
   - List `.pygit/objects/` directory
   - Examine `.pygit/index` file
3. **Use Low-Level Commands**: Test with `hash-object`, `cat-file` for debugging
4. **Run Individual Tests**: `pytest tests/test_file.py::test_function -v`

## Contributing

This project is educational and contributions should focus on:
- **Clarity**: Code should be easy to understand
- **Educational Value**: Features should demonstrate Git concepts
- **Correctness**: Implementations should follow Git standards where applicable
- **Testing**: All features must be thoroughly tested

## Contact & Support

For questions about this codebase:
1. Check existing GitHub issues
2. Review this documentation  
3. Run tests to verify environment
4. Create detailed GitHub issue if needed

---

*This documentation is maintained alongside the codebase. Update when making significant changes.*