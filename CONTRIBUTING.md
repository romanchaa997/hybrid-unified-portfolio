# Contributing to Hybrid Unified Portfolio System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inspiring community. Please read and follow our Code of Conduct:
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs
1. Check if the bug has already been reported in [Issues](https://github.com/romanchaa997/hybrid-unified-portfolio/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Detailed description of the bug
   - Steps to reproduce
   - Expected and actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features
1. Check existing [Issues](https://github.com/romanchaa997/hybrid-unified-portfolio/issues) for similar suggestions
2. Create a new issue with:
   - Clear title describing the feature
   - Use case and motivation
   - Possible implementation approach
   - Examples of how it would work

### Pull Requests

#### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/romanchaa997/hybrid-unified-portfolio.git
cd hybrid-unified-portfolio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools

# Install pre-commit hooks
pre-commit install
```

#### Making Changes
1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes following our code style guidelines
3. Write or update tests for your changes
4. Run tests locally: `pytest`
5. Ensure code formatting: `black src/`
6. Check linting: `pylint src/`

#### Commit Messages
Follow conventional commit format:
```
<type>: <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat: add vector embedding caching mechanism

Implement Redis-based caching for embedding results to improve performance
for frequently accessed skills and projects.

Closes #123
```

#### Submitting a Pull Request
1. Push your branch to your fork
2. Submit a PR with:
   - Clear title describing the changes
   - Description of what changed and why
   - Link to related issues
   - Screenshots for UI changes (if applicable)
3. Ensure all checks pass
4. Respond to review comments
5. Keep the PR focused and manageable in size

## Development Guidelines

### Code Style
- Use PEP 8 style guide
- Use type hints for function parameters and returns
- Write docstrings for classes and functions
- Maximum line length: 100 characters

### Testing
- Write tests for new features
- Maintain >80% code coverage
- Run tests before submitting PR: `pytest --cov=src`
- Use descriptive test names

### Documentation
- Update README.md if adding features
- Update relevant documentation files in `/docs`
- Include docstrings in code
- Add examples for new APIs

## Commit Workflow

1. Fork the repository
2. Create feature branch from `main`
3. Make focused commits
4. Submit PR for review
5. Address review comments
6. Once approved, PR will be merged

## Getting Help

- **Documentation**: Check `/docs` folder
- **Issues**: Browse existing issues for solutions
- **Discussions**: Start a discussion for questions
- **Email**: romanchaa997@gmail.com

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Project documentation

Thank you for contributing to make this project better! 🎉
