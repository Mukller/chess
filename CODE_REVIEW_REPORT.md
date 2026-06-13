# 🔍 Code Review & Security Report — chess

**Дата ревью:** 2026-06-13  
**Ревьюер:** Claude Code (security audit + code quality)  
**Статус:** ⚠️ ТРЕБУЕТ ВНИМАНИЯ

---

## 📊 Сводка

| Категория | Найдено |
|-----------|---------|
| 🔴 Критичные | 2 |
| 🟡 Средние | 3 |
| 🟢 Низкие | 2 |

---

## 🔴 Критичные проблемы

### 1. Небезопасный default для app_secret_key — `backend/app/config.py:18`

**Код:**
```python
app_secret_key: str = Field(default="change-me", min_length=8)
```

**Описание:** Secret key имеет hardcoded default значение "change-me". Это означает что если `.env` не установлен, приложение будет работать с ИЗВЕСТНЫМ ключом!

**Риск:** 🔴 **CRITICAL**
- Любой может подделать JWT токены
- Компрометация аутентификации
- Полная compromised приложения

**Рекомендация:**
```python
app_secret_key: str = Field(default="", min_length=8)  # REQUIRED - no default

@field_validator("app_secret_key", mode="before")
@classmethod
def validate_secret_key(cls, v):
    if not v or v == "change-me":
        raise ValueError("app_secret_key must be set in .env, cannot use default")
    return v
```

**Статус:** ⏳ **Требует внимания** (КРИТИЧНО исправить перед production)

---

### 2. CORS открыт для localhost:3000 hardcoded — `backend/app/config.py:39`

**Код:**
```python
cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
```

**Описание:** CORS origins содержат hardcoded localhost в production коде.

**Риск:** 🔴 **HIGH**
- Может случайно попасть в production
- Cross-Origin уязвимость

**Рекомендация:**
```python
cors_origins: List[str] = Field(
    default_factory=lambda: [] if os.getenv("APP_ENV") == "production" else ["http://localhost:3000"]
)
```

**Статус:** ⏳ **Требует внимания**

---

## 🟡 Средние проблемы

### 3. Отсутствует HTTPS enforcement — `backend/app/config.py` 

**Описание:** Нет обязательного HTTPS в production режиме.

**Рекомендация:** Добавить middleware для redirect HTTP → HTTPS в production.

---

### 4. Rate limiting зависит от конфига — `backend/app/config.py:49`

**Код:**
```python
rate_limit_per_minute: int = 30
```

**Описание:** Rate limiting имеет слабое default значение (30 req/min - это много для API).

**Рекомендация:** Снизить до 10 req/min по умолчанию, особенно для `/move` endpoint.

---

### 5. Нет CSRF protection — отсутствует проверка в code

**Описание:** FastAPI приложение не имеет CSRF tokens для POST запросов.

**Рекомендация:** Добавить CSRF middleware или проверку custom headers.

---

## 🟢 Низкие / стилистические

### 6. JWT algorithm hardcoded как HS256 

**Рекомендация:** Рассмотреть RS256 для лучшей безопасности (хотя HS256 OK для внутренних API).

### 7. Нет логирования попыток forge токенов

**Рекомендация:** Добавить логирование для всех ошибок auth.

---

## ✅ Что сделано хорошо

1. ✅ JWT токены имеют expiration time (24 часа)
2. ✅ Telegram initData properly validated с HMAC-SHA256
3. ✅ FastAPI использует Depends() для инъекции зависимостей (правильно)
4. ✅ Использование Pydantic для валидации данных
5. ✅ Структурированная архитектура (auth, game, engine модули)

---

## 📋 Рекомендации по приоритету

### 🔴 P1 (ИСПРАВИТЬ НЕМЕДЛЕННО)
1. Убрать default secret_key - make it REQUIRED
2. Валидировать что secret_key не "change-me" в production

### 🟠 P2 (ИСПРАВИТЬ ПЕРЕД PRODUCTION)
1. Убрать hardcoded CORS origins для production
2. Добавить HTTPS enforcement
3. Усилить rate limiting для критических endpoints

### 🟡 P3 (УЛУЧШИТЬ)
1. Добавить CSRF protection
2. Добавить логирование для auth ошибок
3. Рассмотреть RS256 вместо HS256

---

## 📝 Заключение

**Оценка:** ⚠️ **REQUIRES FIXES** (не готово к production)

Приложение имеет **2 CRITICAL уязвимости** которые НУЖНО исправить:
1. Default secret_key "change-me" 
2. Hardcoded CORS origins

После исправления этих двух проблем приложение будет безопасным для использования.

---

**Дата последнего обновления:** 2026-06-13
