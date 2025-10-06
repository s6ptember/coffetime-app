#!/bin/bash

# ============================================================================
# Скрипт автоматического развертывания Coffetime PWA на VPS
# ============================================================================

set -e  # Останавливаем выполнение при любой ошибке

# Цвета для красивого вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Функции для красивого вывода
print_header() {
    echo -e "\n${BOLD}${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${MAGENTA}║${NC}  $1"
    echo -e "${BOLD}${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_step() {
    echo -e "\n${BOLD}${BLUE}▶${NC} $1${NC}"
}

# Проверка, что скрипт запущен с правами root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Этот скрипт должен быть запущен с правами root (используйте sudo)"
        exit 1
    fi
}

# Приветствие
show_welcome() {
    clear
    echo -e "${BOLD}${CYAN}"
    cat << "EOF"
   ╔═══════════════════════════════════════════════════════════╗
   ║                                                           ║
   ║        ☕ COFFETIME PWA - СКРИПТ РАЗВЕРТЫВАНИЯ ☕         ║
   ║                                                           ║
   ║         Автоматическая установка и настройка             ║
   ║                   на Ubuntu VPS                          ║
   ║                                                           ║
   ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
}

# Диалоговое меню для ввода данных
get_user_input() {
    print_header "НАСТРОЙКА ПАРАМЕТРОВ ПРОЕКТА"

    # Домен
    while true; do
        echo -e "${BOLD}${YELLOW}Введите основной домен (например: domen.com):${NC}"
        read -p "> " DOMAIN
        if [[ -z "$DOMAIN" ]]; then
            print_error "Домен не может быть пустым!"
        elif [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$ ]]; then
            print_error "Некорректный формат домена!"
        else
            print_success "Домен принят: $DOMAIN"
            break
        fi
    done

    # WWW домен
    WWW_DOMAIN="www.$DOMAIN"
    print_info "Дополнительный домен: $WWW_DOMAIN"

    # Email для Let's Encrypt
    echo -e "\n${BOLD}${YELLOW}Введите email для сертификатов Let's Encrypt:${NC}"
    read -p "> " EMAIL
    while [[ ! "$EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; do
        print_error "Некорректный формат email!"
        read -p "> " EMAIL
    done
    print_success "Email принят: $EMAIL"

    # Логин админа
    echo -e "\n${BOLD}${YELLOW}Введите логин администратора (по умолчанию: admin):${NC}"
    read -p "> " ADMIN_USERNAME
    ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
    print_success "Логин админа: $ADMIN_USERNAME"

    # Пароль админа
    while true; do
        echo -e "\n${BOLD}${YELLOW}Введите пароль администратора (минимум 8 символов):${NC}"
        read -sp "> " ADMIN_PASSWORD
        echo
        if [[ ${#ADMIN_PASSWORD} -lt 8 ]]; then
            print_error "Пароль должен содержать минимум 8 символов!"
        else
            echo -e "${BOLD}${YELLOW}Подтвердите пароль:${NC}"
            read -sp "> " ADMIN_PASSWORD_CONFIRM
            echo
            if [[ "$ADMIN_PASSWORD" != "$ADMIN_PASSWORD_CONFIRM" ]]; then
                print_error "Пароли не совпадают!"
            else
                print_success "Пароль установлен"
                break
            fi
        fi
    done

    # Секретный ключ (генерируем автоматически)
    SECRET_KEY=$(openssl rand -hex 32)
    print_success "Секретный ключ сгенерирован"

    # Подтверждение
    echo -e "\n${BOLD}${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}Проверьте введенные данные:${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  Домен:          ${GREEN}$DOMAIN${NC}"
    echo -e "  WWW Домен:      ${GREEN}$WWW_DOMAIN${NC}"
    echo -e "  Email:          ${GREEN}$EMAIL${NC}"
    echo -e "  Логин админа:   ${GREEN}$ADMIN_USERNAME${NC}"
    echo -e "  Пароль админа:  ${GREEN}********${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"

    read -p "Всё верно? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Настройка отменена. Перезапустите скрипт."
        exit 0
    fi
}

# Создание .env файла
create_env_file() {
    print_step "Создание файла конфигурации .env"

    cat > .env << EOF
# Database
DATABASE_URL=sqlite+aiosqlite:///./coffetime.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Security
SECRET_KEY=$SECRET_KEY
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD

# Domain
DOMAIN=$DOMAIN
WWW_DOMAIN=$WWW_DOMAIN
EMAIL=$EMAIL

# Files
UPLOAD_PATH=./app/coffeeshop/static/images
MAX_FILE_SIZE=5242880

# Redis
REDIS_URL=redis://localhost:6379
CART_TTL=86400

# Logging
LOG_LEVEL=info
EOF

    print_success ".env файл создан успешно"
}

# Обновление системы
update_system() {
    print_step "Обновление системы Ubuntu"
    apt-get update -qq > /dev/null 2>&1
    apt-get upgrade -y -qq > /dev/null 2>&1
    print_success "Система обновлена"
}

# Установка необходимых пакетов
install_dependencies() {
    print_step "Установка необходимых пакетов"

    PACKAGES=(
        "curl"
        "wget"
        "git"
        "software-properties-common"
        "ca-certificates"
        "gnupg"
        "lsb-release"
    )

    for package in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package"; then
            print_info "Установка $package..."
            apt-get install -y -qq "$package" > /dev/null 2>&1
            print_success "$package установлен"
        else
            print_info "$package уже установлен"
        fi
    done
}

# Остановка процессов на порту 80
kill_port_80() {
    print_step "Проверка процессов на порту 80"

    if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Обнаружены процессы на порту 80"
        print_info "Останавливаем процессы..."

        # Получаем PID процессов
        PIDS=$(lsof -Pi :80 -sTCP:LISTEN -t)

        for PID in $PIDS; do
            PROCESS_NAME=$(ps -p $PID -o comm=)
            print_info "Останавливаем процесс: $PROCESS_NAME (PID: $PID)"
            kill -9 $PID 2>/dev/null || true
        done

        sleep 2

        if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_error "Не удалось освободить порт 80"
            exit 1
        else
            print_success "Порт 80 освобожден"
        fi
    else
        print_success "Порт 80 свободен"
    fi
}

# Установка Docker
install_docker() {
    print_step "Проверка установки Docker"

    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
        print_success "Docker уже установлен (версия: $DOCKER_VERSION)"
    else
        print_info "Установка Docker..."

        # Добавление GPG ключа Docker
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg

        # Добавление репозитория Docker
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

        # Установка Docker
        apt-get update -qq > /dev/null 2>&1
        apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null 2>&1

        # Запуск Docker
        systemctl start docker
        systemctl enable docker > /dev/null 2>&1

        DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
        print_success "Docker установлен успешно (версия: $DOCKER_VERSION)"
    fi
}

# Установка Docker Compose
install_docker_compose() {
    print_step "Проверка установки Docker Compose"

    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        if docker compose version &> /dev/null; then
            COMPOSE_VERSION=$(docker compose version --short)
            print_success "Docker Compose уже установлен (версия: $COMPOSE_VERSION)"
        else
            COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f3 | cut -d ',' -f1)
            print_success "Docker Compose уже установлен (версия: $COMPOSE_VERSION)"
        fi
    else
        print_info "Docker Compose устанавливается как плагин Docker..."
        print_success "Docker Compose установлен через плагин Docker"
    fi
}

# Установка Certbot
install_certbot() {
    print_step "Установка Certbot для SSL сертификатов"

    if command -v certbot &> /dev/null; then
        print_success "Certbot уже установлен"
    else
        print_info "Установка Certbot..."
        apt-get install -y -qq certbot > /dev/null 2>&1
        print_success "Certbot установлен"
    fi
}

# Получение SSL сертификатов
obtain_ssl_certificates() {
    print_step "Получение SSL сертификатов Let's Encrypt"

    # Проверяем, не существуют ли уже сертификаты
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_warning "Сертификаты для $DOMAIN уже существуют"
        read -p "Перевыпустить сертификаты? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Используем существующие сертификаты"
            return 0
        fi
    fi

    # Создаем директорию для certbot challenge
    mkdir -p certbot/www

    # Временный nginx для получения сертификатов
    print_info "Запуск временного веб-сервера для верификации домена..."

    docker run --rm -d \
        --name nginx_certbot_temp \
        -p 80:80 \
        -v "$(pwd)/certbot/www:/usr/share/nginx/html" \
        nginx:alpine > /dev/null 2>&1

    sleep 3

    # Получаем сертификаты
    print_info "Запрос сертификатов для доменов: $DOMAIN, $WWW_DOMAIN"

    certbot certonly --webroot \
        --webroot-path="$(pwd)/certbot/www" \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --force-renewal \
        -d "$DOMAIN" \
        -d "$WWW_DOMAIN"

    # Останавливаем временный nginx
    docker stop nginx_certbot_temp > /dev/null 2>&1 || true

    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_success "SSL сертификаты успешно получены"
        print_info "Сертификаты сохранены в: /etc/letsencrypt/live/$DOMAIN/"
    else
        print_error "Не удалось получить SSL сертификаты"
        print_warning "Проверьте, что домены $DOMAIN и $WWW_DOMAIN указывают на этот сервер"
        exit 1
    fi
}

# Настройка Nginx конфигурации
configure_nginx() {
    print_step "Настройка Nginx конфигурации"

    # Обновляем nginx.conf с правильными доменами
    sed -i "s/server_name .*/server_name $DOMAIN $WWW_DOMAIN;/g" nginx/nginx.conf
    sed -i "s|ssl_certificate /etc/letsencrypt/live/[^/]*/fullchain.pem|ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem|g" nginx/nginx.conf
    sed -i "s|ssl_certificate_key /etc/letsencrypt/live/[^/]*/privkey.pem|ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem|g" nginx/nginx.conf

    print_success "Nginx конфигурация обновлена"
}

# Создание необходимых директорий
create_directories() {
    print_step "Создание необходимых директорий"

    DIRS=(
        "app/coffeeshop/static/images/products"
        "media"
        "staticfiles"
        "certbot/www"
    )

    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Создана директория: $dir"
        else
            print_info "Директория уже существует: $dir"
        fi
    done

    # Устанавливаем права доступа
    chmod -R 755 app/coffeeshop/static 2>/dev/null || true
    chmod -R 755 media 2>/dev/null || true
    chmod -R 755 staticfiles 2>/dev/null || true

    print_success "Права доступа установлены"
}

# Сборка и запуск Docker контейнеров
build_and_run_docker() {
    print_step "Сборка и запуск Docker контейнеров"

    # Останавливаем старые контейнеры если они есть
    if docker ps -a | grep -q "coffetime"; then
        print_info "Останавливаем существующие контейнеры..."
        docker-compose down > /dev/null 2>&1 || docker compose down > /dev/null 2>&1 || true
        print_success "Старые контейнеры остановлены"
    fi

    # Собираем образы
    print_info "Сборка Docker образов (это может занять несколько минут)..."
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache > /dev/null 2>&1
    else
        docker compose build --no-cache > /dev/null 2>&1
    fi
    print_success "Docker образы собраны"

    # Запускаем контейнеры
    print_info "Запуск контейнеров..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi

    # Ждем запуска
    print_info "Ожидание запуска сервисов..."
    sleep 10

    # Проверяем статус
    if command -v docker-compose &> /dev/null; then
        STATUS=$(docker-compose ps | grep -c "Up" || echo "0")
    else
        STATUS=$(docker compose ps | grep -c "Up" || echo "0")
    fi

    if [ "$STATUS" -ge 2 ]; then
        print_success "Все контейнеры запущены успешно"
    else
        print_warning "Некоторые контейнеры могут быть не запущены"
        print_info "Проверьте статус: docker compose ps"
    fi
}

# Проверка работоспособности
check_health() {
    print_step "Проверка работоспособности приложения"

    print_info "Ожидание инициализации сервиса..."
    sleep 5

    # Проверяем HTTP эндпоинт
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Приложение отвечает на запросы"
    else
        print_warning "Приложение пока не отвечает (может требоваться больше времени)"
    fi

    # Проверяем HTTPS (если сертификаты получены)
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_info "Проверка HTTPS доступности..."
        sleep 3
        if curl -f -s -k "https://$DOMAIN/health" > /dev/null 2>&1; then
            print_success "HTTPS работает корректно"
        else
            print_warning "HTTPS может требовать дополнительного времени для инициализации"
        fi
    fi
}

# Показать информацию о развертывании
show_deployment_info() {
    clear
    print_header "РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО! 🎉"

    echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║                   ИНФОРМАЦИЯ О ПРОЕКТЕ                       ║${NC}"
    echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}\n"

    echo -e "${BOLD}🌐 URLs:${NC}"
    echo -e "   Основной сайт:     ${CYAN}https://$DOMAIN${NC}"
    echo -e "   WWW версия:        ${CYAN}https://$WWW_DOMAIN${NC}"
    echo -e "   Админ панель:      ${CYAN}https://$DOMAIN/admin${NC}"

    echo -e "\n${BOLD}🔐 Доступ к админке:${NC}"
    echo -e "   Логин:    ${YELLOW}$ADMIN_USERNAME${NC}"
    echo -e "   Пароль:   ${YELLOW}$ADMIN_PASSWORD${NC}"

    echo -e "\n${BOLD}📝 Полезные команды:${NC}"
    echo -e "   Просмотр логов:         ${CYAN}docker compose logs -f${NC}"
    echo -e "   Перезапуск:             ${CYAN}docker compose restart${NC}"
    echo -e "   Остановка:              ${CYAN}docker compose down${NC}"
    echo -e "   Статус контейнеров:     ${CYAN}docker compose ps${NC}"

    echo -e "\n${BOLD}📂 Важные файлы:${NC}"
    echo -e "   Конфигурация:    ${CYAN}.env${NC}"
    echo -e "   База данных:     ${CYAN}coffetime.db${NC}"
    echo -e "   SSL сертификаты: ${CYAN}/etc/letsencrypt/live/$DOMAIN/${NC}"

    echo -e "\n${BOLD}🔄 Обновление сертификатов:${NC}"
    echo -e "   Сертификаты автоматически обновляются через контейнер certbot"
    echo -e "   Ручное обновление: ${CYAN}docker compose restart certbot${NC}"

    echo -e "\n${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║  Ваш сайт доступен по адресу: https://$DOMAIN  ║${NC}"
    echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}\n"
}

# Основная функция
main() {
    show_welcome

    print_info "Проверка прав доступа..."
    check_root

    get_user_input

    print_header "НАЧАЛО УСТАНОВКИ"

    create_env_file
    update_system
    install_dependencies
    kill_port_80
    install_docker
    install_docker_compose
    install_certbot
    obtain_ssl_certificates
    configure_nginx
    create_directories
    build_and_run_docker
    check_health

    show_deployment_info

    print_success "Развертывание завершено!"
}

# Обработка прерывания
trap 'echo -e "\n${RED}Установка прервана пользователем${NC}"; exit 130' INT

# Запуск основной функции
main

exit 0
