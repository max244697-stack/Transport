---
name: plan
description: >-
  План розробки сайту замовлення вантажоперевезень (БусПереїзд). Використовувати
  при плануванні, реалізації або рефакторингу головної сторінки, форми замовлення,
  таблиці розцінок, галереї виконаних замовлень або міграції з магазину меблів.
---

# План: сайт замовлення вантажоперевезень

## Опис продукту

Сайт для замовлення вантажоперевезень. На головній сторінці кнопка «Замовити»; при натисканні — заповнення форми від юзера: номер телефону, обрати тип перевезень та звідки і куди. Нижче — таблиця з розцінками, яку заповнюємо через адмінку. Ще одна вкладка — виконані замовлення з фотографіями виконаних замовлень, які додаються через адмінку.

**Бренд:** БусПереїзд Буча — вантажні перевезення у Бучі, Ірпіні, Гостомелі, Ворзелі, Києві та області.

**Референс UI:** `old/index.html` — hero, вкладки, картки тарифів, контакти (телефон, Telegram, Viber).

---

## Сторінки та секції

### 1. Головна сторінка

| Елемент | Опис |
|---------|------|
| Hero | Назва, підзаголовок з зоною покриття, контакти |
| Кнопка «Замовити» | Відкриває форму (модальне вікно або секція на сторінці) |
| Форма замовлення | Телефон, тип перевезення, звідки, куди |
| Таблиця розцінок | Динамічна, дані з адмінки |
| Вкладки | Мінімум дві: «Ціни» / «Виконані замовлення» (або «Про нас» за потреби) |

### 2. Форма замовлення

**Поля:**

- `phone` — номер телефону (обов'язкове)
- `transport_type` — тип перевезення (вибір зі списку, з адмінки)
- `from_location` — звідки (місто/адреса)
- `to_location` — куди (місто/адреса)

**Поведінка:**

- Валідація на клієнті та сервері
- Після відправки — **збереження в БД** (`TransportOrder`) + **сповіщення в Telegram-бот**
- Повідомлення користувачу про успішне замовлення (toast / flash message)

**Flow відправки:**

1. POST → валідація полів
2. `TransportOrder.objects.create(...)` — зберегти в БД
3. Асинхронно надіслати повідомлення в Telegram (не блокувати відповідь користувачу)
4. Повернути успіх навіть якщо Telegram тимчасово недоступний (логувати помилку)

**Міста:** використати існуючий JSON `static/json/CitiesAndVillages - 14 March.json` та функцію `get_cities_by_region()` у `app/views.py` для автодоповнення або select.

### 3. Таблиця розцінок

Керується через Django Admin. Відображати на головній у вкладці «Ціни».

**Приклад структури (з `old/index.html`):**

- Стандартні: по місту від 500 грн, по області 30 грн/км
- Міста: Ірпінь, Гостомель — від 650 грн
- Послуги: вантажники, упакування — від 300 грн

### 4. Виконані замовлення (галерея)

Окрема вкладка з фото виконаних робіт. Контент додається через адмінку.

**Поля моделі:**

- `title` — короткий опис
- `image` — фото
- `order` — порядок відображення
- `is_published` — показувати на сайті
- `date_completed` — дата (опційно)

---

## Моделі Django

```python
# app/models.py — додати

class TransportType(models.Model):
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

class Tariff(models.Model):
    category = models.CharField(max_length=100)  # напр. «Стандартні», «Міста»
    name = models.CharField(max_length=150)       # напр. «По місту»
    price = models.CharField(max_length=100)    # напр. «від 500 грн»
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

class TransportOrder(models.Model):
    phone = models.CharField(max_length=20)
    transport_type = models.ForeignKey(TransportType, on_delete=models.SET_NULL, null=True)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='new')  # new, in_progress, done

class CompletedOrder(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='completed_orders/')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    date_completed = models.DateField(null=True, blank=True)
```

Зареєструвати всі моделі в `app/admin.py`.

---

## Telegram-сповіщення

Після збереження замовлення в БД — надіслати повідомлення оператору через [Telegram Bot API](https://core.telegram.org/bots/api).

### Env-змінні

| Змінна | Опис |
|--------|------|
| `TELEGRAM_BOT_TOKEN` | Токен бота від [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ID чату/каналу/групи, куди надсилати замовлення |

### Реалізація

- Функція `send_telegram_message(text)` у `app/views.py` або окремому `app/notifications.py`
- HTTP POST на `https://api.telegram.org/bot{TOKEN}/sendMessage`
- Використати `urllib3` (вже є в проєкті) або `requests`
- Обгортка `send_telegram_async()` — аналог `send_mail_async()`, через `Thread`

```python
def send_telegram_message(text):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        raise ValueError('TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured')
    # POST sendMessage з parse_mode=HTML
```

### Формат повідомлення

```
🚚 Нове замовлення #42

📞 Телефон: 093 420 53 20
📦 Тип: Квартирний переїзд
📍 Звідки: Буча, вул. ...
🏁 Куди: Київ, вул. ...
🕐 01.08.2026 11:30
```

### Налаштування бота

1. Створити бота через @BotFather → отримати `TELEGRAM_BOT_TOKEN`
2. Дізнатися `chat_id`: написати боту /start, потім `GET https://api.telegram.org/bot{TOKEN}/getUpdates`
3. Додати змінні в `.env` (dev) та Railway (prod)

---

## Технічний контекст проєкту

| Компонент | Шлях / примітка |
|-----------|-----------------|
| Django app | `app/` |
| Шаблони | `app/templates/app/` |
| Статика | `static/css/`, `static/js/` |
| Старий дизайн перевезень | `old/index.html`, `old/style.css` |
| Сповіщення | Telegram Bot API (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) |
| Async-патерн | `send_mail_async` у `app/views.py` — зразок для `send_telegram_async` |
| Міста UA | `get_cities_by_region()` + JSON у static |

**Поточний стан:** головна (`app/templates/app/index.html`) — каталог меблів. Потрібна заміна або окремий view під перевезення.

---

## Чеклист реалізації

```
Прогрес:
- [ ] Моделі: TransportType, Tariff, TransportOrder, CompletedOrder
- [ ] Міграції та реєстрація в admin
- [ ] View головної з тарифами, галереєю, формою
- [ ] URL та шаблон головної (hero + вкладки + форма)
- [ ] POST endpoint для форми: збереження в БД + Telegram-сповіщення
- [ ] `send_telegram_message` / `send_telegram_async` + env-змінні
- [ ] Стилі (адаптувати old/style.css або інтегрувати в static/css/)
- [ ] Навігація: прибрати/замінити посилання на магазин меблів
- [ ] Тести форми та admin CRUD
```

---

## Пріоритети

1. **MVP:** головна + форма + таблиця цін з адмінки
2. **Другий етап:** галерея виконаних замовлень
3. **Опційно:** SEO-контент з `old/index.html` (вкладка «Про нас»)

---

## Обмеження

- Мова інтерфейсу: **українська**
- Не ламати існуючу інфраструктуру (Railway deploy, gunicorn)
- Мінімальний diff — перевикористовувати `get_cities_by_region()`, async-патерн з views, base template
- Telegram-токен і chat_id — тільки через env, не комітити в репозиторій
- Адмінка — єдине джерело правди для тарифів і галереї
