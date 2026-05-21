# Contributing

Спасибо, что хотите внести вклад в **Telegram Chess Bot**! Этот документ описывает,
как открывать issue, оформлять PR и какие соглашения мы используем в коде.

> 🇬🇧 English version below.

---

## 🐛 Reporting bugs / 🚀 Feature requests

1. Перед созданием issue — найдите похожее в [issues](https://github.com/Mukller/chess/issues).
2. Используйте говорящий заголовок: `[bug] WebSocket теряет подключение после 60 секунд`.
3. Для багов укажите:
   - Шаги воспроизведения
   - Ожидаемое и фактическое поведение
   - Версии (Docker, Telegram-клиент, браузер)
   - Логи (`docker compose logs api` / `frontend`)
4. Для feature requests опишите проблему, которую вы решаете, и предложите API/UX.

---

## 🌿 Workflow

Мы используем GitHub Flow:

1. **Форкните** репозиторий или создайте ветку от `main`.
2. Назовите ветку говоряще: `feat/pvp-mode`, `fix/ws-reconnect`, `docs/api-examples`.
3. Делайте маленькие, осмысленные коммиты.
4. Перед PR прогоните локально:
   ```bash
   # backend
   ruff check backend/app
   mypy backend/app  # если настроено
   # frontend
   cd frontend && npm run build
   ```
5. Откройте PR в `main` с описанием:
   - Что меняется и почему
   - Как протестировать
   - Скриншоты для UI-изменений
6. PR должен пройти review и CI (если настроен).

### Conventional commits

Мы рекомендуем (но не требуем) [conventional commits](https://www.conventionalcommits.org/ru/):

- `feat: add ELO rating`
- `fix(ws): reconnect on 1006 close code`
- `docs(readme): document hint endpoint`
- `refactor(engine): extract DifficultyProfile`
- `chore(deps): bump aiogram to 3.16`

---

## 🧱 Code style

### Backend (Python)

- Python 3.12+, тайпхинты обязательны для публичных функций
- Форматирование: `ruff format` (settings совместимы с `black`)
- Линтер: `ruff check` (без `--fix` в CI)
- Никаких голых `except` — ловите конкретные исключения
- Async-функции не делают блокирующий I/O (без `time.sleep`, синхронных HTTP)
- Сервисы (`GameService`, `EnginePool`) не должны знать про FastAPI request/response

### Frontend (TypeScript / React)

- Strict mode (`strict: true` в `tsconfig`)
- Функциональные компоненты, без классов
- Бизнес-логика → хуки (`useGameSocket`, `useTelegram`), а не в JSX
- Zustand stores маленькие и сфокусированные
- Tailwind utility-classes; глобальные CSS-переменные приходят из Telegram theme

### Тесты

- Backend: `pytest` + `pytest-asyncio` (тесты живут в `backend/tests/`)
- Каждое исправление бага сопровождайте регрессионным тестом
- Не мокайте `python-chess` — это эталон правил шахмат

---

## 🔐 Security disclosures

Не публикуйте уязвимости в публичных issue. Напишите maintainer'у через
[GitHub profile](https://github.com/Mukller) или сделайте приватный security advisory.

---

## 📜 License

Контрибутя в этот проект, вы соглашаетесь с тем, что ваши изменения будут лицензированы под [MIT License](LICENSE.md).

---

## 🇬🇧 English

### Getting Started

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/chess.git
   cd chess
   git remote add upstream https://github.com/Mukller/chess.git
   ```

2. **Create a Branch**
   ```bash
   git fetch upstream && git checkout main && git merge upstream/main
   git checkout -b feat/your-feature-name
   # or: git checkout -b fix/your-bug-name
   ```

3. **Setup Development Environment**
   - See [QUICK_START.md](QUICK_START.md) for detailed setup
   - Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
   - Frontend: `cd frontend && npm install && npm run dev`
   - Ensure Redis is running

4. **Make Your Changes**
   - Write clean, well-documented code
   - Include tests for new features and bug fixes
   - Follow the code style guidelines below

5. **Test Locally**
   ```bash
   # Backend tests
   cd backend && pytest tests/ && ruff check app/ && mypy app/
   
   # Frontend tests
   cd frontend && npm test && npm run build
   ```

6. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: add description of your change"
   git push origin feat/your-feature-name
   ```

7. **Open Pull Request**
   - Go to https://github.com/Mukller/chess
   - Click "New Pull Request" and select your branch
   - Fill in the PR template with clear description
   - Reference any related issues with `#123`

### Pull Request Template

```markdown
## Description
What does this PR do?

## Type
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Performance improvement

## Testing
How did you test this? Steps to reproduce:
1. ...
2. ...

## Screenshots (if UI changes)
Add screenshots for visual changes

## Checklist
- [ ] Tests added/updated
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Code Style

**Backend (Python)**:
- Type hints required for all public functions
- Use `ruff format` (or `black`) for formatting
- Use `ruff check` for linting
- Specific exception handling (no bare `except`)
- No blocking I/O in async functions
- Services independent of FastAPI

**Frontend (TypeScript/React)**:
- TypeScript strict mode enabled
- Functional components with hooks only
- Business logic in custom hooks
- Zustand stores for state management
- Tailwind CSS for styling

**Testing**:
- pytest + pytest-asyncio for backend
- New features require tests
- Bug fixes require regression tests
- Don't mock python-chess (use real rules)
- Aim for >80% code coverage

### Commit Message Format

Follow [conventional commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body (optional)>

<footer (optional)>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Scopes**: `api`, `bot`, `game`, `frontend`, `docker`, `redis`

**Examples**:
- `feat(game): add castling move validation`
- `fix(bot): handle missing state gracefully`
- `docs(api): add WebSocket examples`
- `refactor(storage): extract Redis key formatting`
- `test(game): add ELO calculation tests`

### Running Tests

```bash
# Backend
cd backend
pytest tests/                    # All tests
pytest tests/game/              # Single directory
pytest tests/game/test_service.py::test_create_game  # Single test
pytest -v                        # Verbose
pytest --cov=app                # With coverage

# Frontend
cd frontend
npm test                         # Run all tests
npm test Board                   # Single test file
npm test -- --watch             # Watch mode
npm test -- --coverage          # Coverage report
```

### Common Issues

**"Tests failing"**
```bash
# Run with verbose output to see actual errors
pytest -v tests/

# Clear cache
rm -rf __pycache__ .pytest_cache
pip install -r requirements.txt -r requirements-dev.txt
```

**"Type checking errors"**
```bash
mypy backend/app --pretty
```

**"Linting issues"**
```bash
# Show issues
ruff check backend/app

# Auto-fix
ruff check backend/app --fix
ruff format backend/app
```

**"Port already in use"**
```bash
# Find process (Linux/Mac)
lsof -i :8000
# Or (Windows)
netstat -ano | findstr :8000

# Use different port
uvicorn app.main:app --port 8001
```

### Documentation

- Add docstrings to all public functions
- Update README.md if behavior changes
- Update API_REFERENCE.md for new endpoints
- Add examples in QUICK_START.md if applicable

### Performance

**Backend**:
- ✅ Use async/await for I/O
- ✅ Cache computed results
- ✅ Use connection pooling
- ❌ No blocking I/O in async functions

**Frontend**:
- ✅ Use React.memo for expensive components
- ✅ Lazy-load large components
- ✅ Code-split at routes
- ❌ Avoid unnecessary re-renders

### Security

**API**:
- ✅ Validate all user input
- ✅ Use python-chess for move validation
- ✅ Verify JWT tokens
- ✅ Rate limit per user
- ❌ Don't trust client data
- ❌ Don't expose internal errors

**Frontend**:
- ✅ Sanitize user content
- ✅ Use HTTPS
- ✅ Validate API responses
- ❌ No sensitive data in URLs
- ❌ No eval() on user input

### Release Process

Only maintainers create releases. Versions follow [SemVer](https://semver.org/):
- `MAJOR` — breaking changes
- `MINOR` — new features (backward compatible)
- `PATCH` — bug fixes

Example: `v1.2.3`

### Security Disclosures

**Do not** file public issues for security vulnerabilities. Contact the maintainer privately:
- GitHub profile: https://github.com/Mukller
- Or create a private security advisory

### Code of Conduct

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### License

By contributing, you agree your work will be licensed under the [MIT License](LICENSE.md).

### Resources

- [QUICK_START.md](QUICK_START.md) — Local development setup
- [API_REFERENCE.md](API_REFERENCE.md) — REST API documentation
- [FRONTEND_SETUP.md](FRONTEND_SETUP.md) — React/TypeScript guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues
- [Python Style Guide](https://pep8.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Documentation](https://react.dev)

### Questions?

- Check [GitHub Issues](https://github.com/Mukller/chess/issues)
- See [GitHub Discussions](https://github.com/Mukller/chess/discussions)
- Review project documentation

Thank you for contributing! 🙏
