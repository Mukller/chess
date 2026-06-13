# Руководство для контрибьютеров

Спасибо за интерес к проекту! Этот документ описывает процесс внесения вклада.

## 📋 Содержание

- [Кодекс поведения](#кодекс-поведения)
- [Как начать](#как-начать)
- [Стиль кода](#стиль-кода)
- [Коммиты](#коммиты)
- [Pull Requests](#pull-requests)
- [Тестирование](#тестирование)

## 🤝 Кодекс поведения

Мы придерживаемся принципов вежливости и уважения. Ожидаем того же от всех участников:

- Будь вежлив и уважителен в общении
- Принимай конструктивную критику
- Сосредоточься на том, что лучше для сообщества
- Проявляй сочувствие к другим участникам

## 🚀 Как начать

### 1. Форкни репозиторий

Нажми кнопку **Fork** на странице репозитория.

### 2. Клонируй свой форк

```bash
git clone https://github.com/YOUR_USERNAME/AdvancedSpyInventory.git
cd AdvancedSpyInventory
```

### 3. Добавь upstream (оригинальный репозиторий)

```bash
git remote add upstream https://github.com/Mukller/AdvancedSpyInventory.git
```

### 4. Создай ветку

```bash
# Обновись с оригинального репозитория
git fetch upstream
git checkout -b feature/description upstream/main

# Или для исправления багов:
git checkout -b bugfix/description upstream/main
```

**Правила именования веток:**
- `feature/name-of-feature` — новые функции
- `bugfix/name-of-bug` — исправление ошибок
- `docs/description` — документация
- `refactor/description` — рефакторинг кода

## 💻 Стиль кода

### Java код

```java
// ✅ ПРАВИЛЬНО
public class InventoryViewer {
    private final SpyPlugin plugin;
    private Player targetPlayer;

    public InventoryViewer(SpyPlugin plugin, Player targetPlayer) {
        this.plugin = plugin;
        this.targetPlayer = targetPlayer;
    }

    public void openInventory() {
        if (targetPlayer != null) {
            // Логика открытия инвентаря
        }
    }
}

// ❌ НЕПРАВИЛЬНО
public class InventoryViewer{
public final SpyPlugin plugin;
public Player p;
public InventoryViewer(SpyPlugin p,Player tp){plugin=p;p=tp;}
public void open(){if(p!=null){}}
```

### Требования к коду

- Используй **camelCase** для переменных и методов
- Используй **PascalCase** для классов
- Максимум **100 символов** в строке
- Отступ — **4 пробела** (или tab, см. конфиг проекта)
- Добавляй JavaDoc комментарии к публичным методам:

```java
/**
 * Открывает инвентарь целевого игрока для администратора.
 *
 * @param admin администратор, просматривающий инвентарь
 * @param target целевой игрок
 * @return true если инвентарь успешно открыт, иначе false
 */
public boolean openInventoryForAdmin(Player admin, Player target) {
    // ...
}
```

### YAML конфигурация

```yaml
# ✅ ПРАВИЛЬНО
plugin:
  name: "AdvancedSpyInventory"
  enabled: true
  
  settings:
    # Уведомлять игрока о просмотре инвентаря
    notify-player: true
    logging: true

# ❌ НЕПРАВИЛЬНО
plugin:
name: AdvancedSpyInventory
enabled: yes
settings: {notify: true, logging: true}
```

## 📝 Коммиты

Используй понятные сообщения коммитов:

```bash
# ✅ ПРАВИЛЬНО
git commit -m "feat: Add inventory open command with permission checks"
git commit -m "fix: Correct player offline detection bug"
git commit -m "docs: Update README with installation instructions"
git commit -m "refactor: Simplify InventoryManager code"

# ❌ НЕПРАВИЛЬНО
git commit -m "fix bug"
git commit -m "update"
git commit -m "asdf"
```

**Формат:** `<type>: <subject>`

**Типы:**
- `feat` — новая функция
- `fix` — исправление ошибки
- `docs` — обновление документации
- `refactor` — переписывание кода без смены функционала
- `test` — добавление или обновление тестов
- `perf` — улучшение производительности

## 🔄 Pull Requests

### Перед созданием PR

1. ✅ Убедись, что код компилируется без ошибок
2. ✅ Протестируй функцию на игровом сервере
3. ✅ Обновись с `upstream/main`
4. ✅ Удали лишние коммиты (`git rebase`)

### Создание PR

```bash
# Запушь свою ветку
git push origin feature/your-feature

# Перейди на GitHub и создай Pull Request
```

### Описание PR

```markdown
## Описание
Краткое описание того, что делает PR.

## Тип изменения
- [ ] Новая функция
- [x] Исправление ошибки
- [ ] Breaking change
- [ ] Обновление документации

## Как это тестировалось?
Опишите, как ты тестировал изменения:
1. Запустил сервер на версии X.X.X
2. Выполнил команду `/spy PlayerName`
3. Проверил логи

## Чек-лист
- [x] Мой код следует стилю проекта
- [x] Я провел самопроверку
- [x] Я обновил документацию (если нужно)
- [x] Код компилируется без ошибок
```

## 🧪 Тестирование

### Локальное тестирование

1. Скомпилируй плагин:
```bash
mvn clean package
# или gradle build
```

2. Скопируй JAR в тестовый сервер:
```bash
cp target/AdvancedSpyInventory-*.jar ~/test-server/plugins/
```

3. Запусти сервер и протестируй функцию

### Что нужно тестировать

- ✅ Команда `/spy <player>` работает
- ✅ Команда не работает без разрешений
- ✅ Плагин корректно обрабатывает оффлайн игроков
- ✅ Конфиг правильно загружается
- ✅ Нет ошибок в консоли

## 📖 Документация

При добавлении новой функции обновляй документацию:

- **README.md** — основное описание
- **CHANGELOG.md** — если существует
- **Inline комментарии** — в самом коде

## ❓ Вопросы?

Если у тебя есть вопросы:

1. Проверь существующие [Issues](https://github.com/Mukller/AdvancedSpyInventory/issues)
2. Создай новый Issue с пометкой `question`
3. Обратись в Discussions (если включены)

## 🎉 Спасибо!

Большое спасибо за внесение вклада в проект! Каждый вклад важен для сообщества.

---

**Happy Coding!** 💻