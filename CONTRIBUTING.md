# Contributing Guide

Thank you for interest in contributing! Read [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) first.

## Setup

```bash
git clone https://github.com/Mukller/chess
cd chess
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development

1. Create feature branch: `git checkout -b feature/name`
2. Make changes
3. Test: `python main.py`
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/name`
6. Create Pull Request

## Commit Format

```
<type>: <description>
```

Types: feat, fix, docs, refactor, test, chore

## Code Style

- Follow PEP 8
- No hardcoded secrets
- Add docstrings for functions

## Testing

- Test locally with bot
- Ensure no breaking changes
- Update README if needed

## Questions?

Open an Issue or Discussion.

Thank you! 🚀