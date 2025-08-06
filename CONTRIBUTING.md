# Contributing to Aircraft Go-Around Tracker

Thank you for your interest in contributing to Aircraft Go-Around Tracker! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/challgren/aircraft-goaround/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - System information (OS, Python version, Docker version if applicable)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case
4. Explain why it would be valuable to the project

### Submitting Code

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/aircraft-goaround.git
cd aircraft-goaround

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 pytest
```

#### Development Workflow

1. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Test your changes:

   ```bash
   # Run the application
   python go_around_tracker.py --test
   
   # Format code
   black go_around_tracker.py
   
   # Check code style
   flake8 go_around_tracker.py
   ```

4. Commit your changes:

   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Coding Standards

### Python Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and under 50 lines when possible
- Use type hints where appropriate

### Code Organization

```python
# Good example
def detect_go_around(positions: List[Position]) -> GoAroundDetection:
    """
    Detect if aircraft is performing a go-around maneuver.
    
    Args:
        positions: List of aircraft positions with altitude and vertical rate
        
    Returns:
        GoAroundDetection object with confidence score
    """
    # Implementation here
    pass
```

### Commit Messages

Use clear, descriptive commit messages:

- `Add: new feature description`
- `Fix: bug description`
- `Update: component description`
- `Refactor: what was refactored`
- `Docs: what documentation was updated`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=go_around_tracker

# Run specific test file
pytest tests/test_detection.py
```

### Writing Tests

Create test files in the `tests/` directory:

```python
def test_go_around_detection():
    """Test go-around detection algorithm."""
    detector = GoAroundDetector()
    aircraft = create_test_aircraft_with_go_around()
    result = detector.detect_go_around(aircraft)
    assert result.is_go_around == True
    assert result.confidence >= 0.6
```

## Docker Development

### Building Local Image

```bash
# Build for testing
docker build -t aircraft-goaround:dev .

# Run local build
docker run -it --rm \
  -p 8889:8889 \
  -e TAR1090_URL=http://your-tar1090:80 \
  aircraft-goaround:dev
```

### Multi-Architecture Build

```bash
# Setup buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t aircraft-goaround:dev \
  .
```

## Documentation

### Updating Documentation

- Keep README.md up to date with new features
- Add docstrings to all new functions
- Update configuration tables when adding new options
- Include examples for new features

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Update the changelog

## Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Update documentation
   - Add entry to CHANGELOG.md
   - Verify Docker build works

2. **PR Description Should Include**
   - Summary of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

3. **Review Process**
   - PRs require at least one review
   - Address all feedback
   - Ensure CI checks pass
   - Squash commits if requested

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release PR
4. After merge, tag release
5. Docker images auto-build on tag

## Getting Help

- Join [SDR-Enthusiasts Discord](https://discord.gg/sTf9uYF)
- Ask questions in GitHub Issues
- Check existing documentation

## Recognition

Contributors will be recognized in:

- README.md acknowledgments
- Release notes
- Project documentation

Thank you for contributing to Aircraft Go-Around Tracker!