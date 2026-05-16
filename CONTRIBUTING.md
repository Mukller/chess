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

We use GitHub Flow:

1. Fork the repo or branch off `main`.
2. Use descriptive branch names (`feat/pvp-mode`, `fix/ws-reconnect`).
3. Keep commits small and focused; conventional commits are appreciated.
4. Run linters / build locally before opening a PR.
5. Open a PR against `main` with a clear description, test plan, and screenshots for UI changes.
6. Be polite and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

For security issues, contact the maintainer privately — do not file a public issue.

By contributing you agree that your work is licensed under the project's [MIT License](LICENSE.md).
