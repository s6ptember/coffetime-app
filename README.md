# ☕ Coffetime PWA - Прогрессивное веб-приложение для кофейни

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.117+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/PWA-Ready-orange.svg" alt="PWA">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/HTMX-Powered-purple.svg" alt="HTMX">
  <img src="https://img.shields.io/badge/Alpine.js-3.x-8BC0D0.svg" alt="Alpine.js">
</div>

## 📱 О проекте

**Coffetime PWA** - это современное прогрессивное веб-приложение для кофейни, которое работает как нативное мобильное приложение. Проект создан с использованием FastAPI на бэкенде и современного стека HTMX + Alpine.js на фронтенде, что обеспечивает молниеносную скорость работы без необходимости в тяжелых JavaScript фреймворках.

### 🎯 Ключевые особенности PWA

- **📲 Установка на главный экран** - работает как нативное приложение на iOS и Android
- **🔄 Офлайн-режим** - базовый функционал доступен без интернета благодаря Service Worker
- **⚡ Мгновенная загрузка** - кэширование статики и оптимизированная производительность
- **📱 Адаптивный дизайн** - идеально выглядит на любых устройствах
- **🔔 Push-уведомления** - поддержка нативных уведомлений (в разработке)
- **🎨 Splash-экраны** - красивые заставки при запуске на iOS/Android
- **👆 Жесты и свайпы** - нативная навигация между разделами

## 🚀 Возможности

### Для клиентов
- 🛒 **Интуитивная корзина** с анимациями и жестами
- ☕ **Каталог продуктов** с фильтрацией по категориям
- 📱 **Выбор размеров** напитков с удобным интерфейсом
- 🔍 **Поиск** по меню в реальном времени
- 📦 **Оформление заказов** с выбором времени готовности
- 👤 **Профиль пользователя** (в разработке)

### Для администратора
- 📊 **Панель управления** с аналитикой
- 🏷️ **Управление категориями** товаров
- ☕ **Управление продуктами** с загрузкой изображений
- 📏 **Настройка размеров** и цен
- 📋 **Управление заказами**
- 🔐 **Защищенный доступ** через HTTP Basic Auth

## 🛠 Технологический стек

### Backend
- **FastAPI** - современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с поддержкой async/await
- **Pydantic** - валидация данных
- **aiosqlite** - асинхронная работа с SQLite
- **Jinja2** - шаблонизатор

### Frontend
- **HTMX** - динамические обновления без JavaScript
- **Alpine.js** - реактивность и интерактивность
- **Tailwind CSS** - утилитарные CSS классы
- **Service Worker** - офлайн функциональность

### DevOps
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy и SSL
- **Let's Encrypt** - бесплатные SSL сертификаты
- **GitHub Actions** - CI/CD (опционально)

## 📦 Установка

### Быстрый старт (локально)

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/coffetime-pwa.git
cd coffetime-pwa

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
# Отредактируйте .env файл

# Запуск приложения
python main.py
```

Приложение будет доступно по адресу: http://localhost:8000

### 🚢 Развертывание на VPS (Production)

#### Автоматическое развертывание

```bash
# Загрузите проект на сервер
scp -r coffetime-pwa root@your-server:/root/

# Подключитесь к серверу
ssh root@your-server

# Перейдите в директорию проекта
cd /root/coffetime-pwa

# Запустите скрипт автоматического развертывания
sudo bash deploy.sh
```

Скрипт автоматически:
- ✅ Установит Docker и Docker Compose
- ✅ Получит SSL сертификаты Let's Encrypt
- ✅ Настроит Nginx
- ✅ Создаст необходимые директории
- ✅ Запустит все контейнеры

#### Ручное развертывание с Docker

```bash
# Создайте .env файл
nano .env

# Добавьте переменные окружения
DATABASE_URL=sqlite+aiosqlite:///./coffetime.db
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
DOMAIN=yourdomain.com
WWW_DOMAIN=www.yourdomain.com
EMAIL=admin@yourdomain.com

# Запустите контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# База данных
DATABASE_URL=sqlite+aiosqlite:///./coffetime.db

# Сервер
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Безопасность
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password

# Домен (для SSL)
DOMAIN=yourdomain.com
WWW_DOMAIN=www.yourdomain.com
EMAIL=admin@yourdomain.com

# Файлы
UPLOAD_PATH=./app/coffeeshop/static/images
MAX_FILE_SIZE=5242880

# Redis (опционально)
REDIS_URL=redis://localhost:6379
CART_TTL=86400

# Логирование
LOG_LEVEL=info
```

## 📱 PWA Функциональность

### Установка на устройство

#### iOS (Safari)
1. Откройте сайт в Safari
2. Нажмите кнопку "Поделиться"
3. Выберите "На экран Домой"
4. Подтвердите установку

#### Android (Chrome)
1. Откройте сайт в Chrome
2. Нажмите на баннер установки или меню (три точки)
3. Выберите "Добавить на главный экран"
4. Подтвердите установку

### Service Worker возможности

- **Кэширование статики** - изображения, стили, скрипты
- **Офлайн страница** - базовый интерфейс без интернета
- **Фоновая синхронизация** - отправка заказов при восстановлении связи
- **Обновление кэша** - автоматическое обновление при новых версиях

## 🎨 Кастомизация

### Генерация иконок и splash-экранов

```bash
# Установите Pillow
pip install pillow

# Сгенерируйте все иконки из одного изображения
python generate_icons.py your-logo.png
```

### Изменение цветовой схемы

Отредактируйте цвета в `tailwind.config` в шаблонах:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'coffee-yellow': '#FED728',
                'coffee-gray': '#E3E8EF',
                'coffee-black': '#0D121C',
                'coffee-purple': '#7A5AF8',
                'coffee-purple-light': '#EBE9FE'
            }
        }
    }
}
```

### Основные эндпоинты

```http
GET     /                      # Главная страница PWA
GET     /health               # Проверка работоспособности
GET     /catalog/products     # Список продуктов
GET     /catalog/categories   # Список категорий
POST    /cart/add            # Добавление в корзину
GET     /cart                # Просмотр корзины
POST    /orders              # Создание заказа
GET     /admin               # Панель администратора
```

## 🔧 Управление

### Docker команды

```bash
# Просмотр логов
docker-compose logs -f

# Перезапуск сервисов
docker-compose restart

# Остановка
docker-compose down

# Пересборка с обновлениями
docker-compose up -d --build
```

### Обновление SSL сертификатов

Сертификаты обновляются автоматически через контейнер certbot.

Ручное обновление:
```bash
docker-compose restart certbot
```


## 📞 Контакты

- Telegram: @svgformat
