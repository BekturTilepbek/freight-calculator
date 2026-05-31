# Деплой FreightFlow на VPS (Aeza)

Полный гайд от заказа сервера до работающего публичного URL.

## Содержание

1. [Заказ VPS на Aeza](#1-заказ-vps-на-aeza)
2. [Первое подключение и базовая настройка](#2-первое-подключение-и-базовая-настройка)
3. [Установка Docker](#3-установка-docker)
4. [Подготовка проекта на GitHub](#4-подготовка-проекта-на-github)
5. [Перенос проекта на сервер](#5-перенос-проекта-на-сервер)
6. [Настройка production-окружения](#6-настройка-production-окружения)
7. [Первый запуск](#7-первый-запуск)
8. [Проверка работоспособности](#8-проверка-работоспособности)
9. [Опционально: домен и HTTPS](#9-опционально-домен-и-https)
10. [Полезные команды на сервере](#10-полезные-команды-на-сервере)
11. [Что делать после защиты](#11-что-делать-после-защиты)

---

## 1. Заказ VPS на Aeza

### Какой тариф брать

Минимальные требования для проекта:
- **CPU:** 1-2 ядра
- **RAM:** 1-2 GB (можно 1 GB, но впритык — 2 GB безопаснее)
- **Диск:** 10-20 GB SSD
- **ОС:** Ubuntu 22.04 LTS или 24.04 LTS

На aeza.net подойдет любой младший тариф из линейки "AEZA Premium" или "AEZA Start". Конкретно сейчас (на 2026 год) это что-то в районе 200-400₽/месяц. Если защита через 1-2 недели — можешь взять с почасовой оплатой и заплатить копейки.

### Что выбрать при заказе

- **Локация:** Россия (Москва) или Германия — без разницы, обе будут работать. Германия чуть дешевле обычно.
- **ОС:** Ubuntu 24.04 LTS
- **SSH-ключ:** если есть — добавь, если нет — Aeza сгенерирует root-пароль и пришлет на email
- **Дополнительно:** ничего не нужно — никаких бэкапов, дополнительных IP и т.д.

После оплаты на email придет письмо с IP-адресом сервера и паролем root (или подтверждение SSH-ключа).

---

## 2. Первое подключение и базовая настройка

### Подключение по SSH

С твоего ноутбука (PowerShell или Git Bash на Windows, Terminal на macOS):

```bash
ssh root@<IP_ТВОЕГО_СЕРВЕРА>
```

Если запросит пароль — введи тот, что прислала Aeza.

### Обновление системы

Первое, что делаем на любом новом сервере:

```bash
apt update && apt upgrade -y
```

Это займет 1-2 минуты.

### Создание непривилегированного пользователя (опционально, но рекомендую)

Работать под root небезопасно. Создадим отдельного пользователя:

```bash
adduser freightflow
# Задай пароль (запиши куда-нибудь)
# Остальные поля можешь пропускать через Enter

# Даем sudo-права
usermod -aG sudo freightflow

# Копируем настройки SSH (если входил по ключу)
mkdir -p /home/freightflow/.ssh
cp ~/.ssh/authorized_keys /home/freightflow/.ssh/ 2>/dev/null || true
chown -R freightflow:freightflow /home/freightflow/.ssh
chmod 700 /home/freightflow/.ssh
chmod 600 /home/freightflow/.ssh/authorized_keys 2>/dev/null || true
```

Переключаемся под нового пользователя:

```bash
su - freightflow
```

Далее все команды выполняем под `freightflow`. Если потребуются root-права — `sudo`.

### Установка базовых утилит

```bash
sudo apt install -y curl git nano ufw
```

### (Опционально) Настройка файрвола

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

Это разрешит только HTTP, HTTPS и SSH. Все остальное будет блокироваться.

---

## 3. Установка Docker

Официальный скрипт от Docker — самый простой способ:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

Добавляем нашего пользователя в группу docker (чтобы не писать sudo перед каждой командой):

```bash
sudo usermod -aG docker freightflow
```

**Важно:** чтобы это применилось, нужно **перелогиниться**:

```bash
exit  # выходим из пользовательской сессии
exit  # выходим из root SSH
ssh freightflow@<IP>  # заходим заново
```

Проверяем, что Docker работает:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

Последняя команда должна вывести «Hello from Docker!». Если да — все ок.

---

## 4. Подготовка проекта на GitHub

Перед переносом убедись, что все последние изменения залиты на GitHub:

На своем ноутбуке:

```bash
git status                   # должно быть "nothing to commit"
git push                     # все запушено
```

Если в `.gitignore` есть `.env` — он не попадет в репозиторий, и это правильно. Production-конфиг создадим прямо на сервере.

### Положи в репозиторий production-файлы

Эти файлы (которые я сейчас тебе передаю) должны быть в репозитории до клонирования на сервер. Скачай их и положи в нужные места:

```
freight-calculator/
├── docker-compose.prod.yml         ← в корень
├── backend/
│   └── Dockerfile.prod              ← в папку backend
└── frontend/
    ├── Dockerfile.prod              ← в папку frontend
    └── nginx.conf                   ← в папку frontend
```

Затем коммит и пуш:

```bash
git add docker-compose.prod.yml backend/Dockerfile.prod frontend/Dockerfile.prod frontend/nginx.conf
git commit -m "chore: add production deployment configuration"
git push
```

---

## 5. Перенос проекта на сервер

На сервере клонируем репозиторий:

```bash
cd ~
git clone https://github.com/<твой_username>/freight-calculator.git
cd freight-calculator
```

Если репозиторий приватный — настрой Deploy Key или личный токен GitHub. Самый простой вариант — сделать репозиторий публичным на время защиты, потом вернуть приватность.

---

## 6. Настройка production-окружения

### Создаем `.env` на сервере

`.env` НЕ в git, его нужно создать на сервере отдельно:

```bash
cp .env.example .env
nano .env
```

Заполни так:

```env
# PostgreSQL — обязательно поставь СТРОНГ-пароль!
POSTGRES_USER=freight_user
POSTGRES_PASSWORD=<СГЕНЕРИРУЙ_СЛУЧАЙНЫЙ_ПАРОЛЬ>
POSTGRES_DB=freight_db

# JWT — критически важный секрет! Сгенерируй случайную строку из 40+ символов.
JWT_SECRET=<СГЕНЕРИРУЙ_СЛУЧАЙНУЮ_СТРОКУ>
```

Для генерации сильных секретов выполни прямо на сервере:

```bash
# Для PostgreSQL пароля (24 символа)
openssl rand -base64 24

# Для JWT_SECRET (48 символов)
openssl rand -base64 48
```

Скопируй вывод в `.env`.

Сохрани и закрой nano: `Ctrl+O`, `Enter`, `Ctrl+X`.

**Проверь, что .env правильно создан:**

```bash
cat .env
```

Не должно быть пустых паролей или плейсхолдеров вроде `<...>`.

---

## 7. Первый запуск

Собираем и запускаем все сервисы:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Это займет 3-5 минут (надо скачать образы, собрать фронт через Vite, поставить зависимости). Следи за прогрессом.

Проверь статус контейнеров:

```bash
docker compose -f docker-compose.prod.yml ps
```

Все три сервиса должны быть `Up`:
- `freightflow_postgres_prod` (healthy)
- `freightflow_backend_prod` (Up)
- `freightflow_frontend_prod` (Up)

Если что-то не стартовало — смотри логи:

```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
```

### Применяем миграции БД

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

Должно вывести что-то вроде `Running upgrade  -> abc123, initial schema`.

### Заполняем тестовыми данными (для демо на защите)

```bash
docker compose -f docker-compose.prod.yml exec backend python -m app.db.seed
```

Должно вывести: «✅ Создано: 3 пользователя, 5 клиентов, 3 брокеров, 3 ТС, 40 заявок».

---

## 8. Проверка работоспособности

Открой в браузере:

```
http://<IP_ТВОЕГО_СЕРВЕРА>
```

Должен открыться лендинг FreightFlow. Зайди:
- → Войти → Демо-кнопка «Диспетчер»
- → Должен открыться дашборд со всеми графиками
- → Проверь калькулятор: введи адреса, нажми «Найти маршрут» — должна загрузиться карта

Все должно работать **точно так же, как локально**. Если что-то отличается — смотри логи (см. раздел 10).

### Swagger в проде

Доступен по `http://<IP>/docs` — для демонстрации API на защите.

---

## 9. Опционально: домен и HTTPS

Если хочешь публичный URL вместо IP — нужен домен и SSL.

### Бесплатные варианты домена для диплома

- **DuckDNS** (duckdns.org) — бесплатный поддомен вроде `freightflow.duckdns.org`
- **sslip.io** — еще проще: автоматически работает с IP, типа `<IP>.sslip.io` сразу резолвится

### Самое быстрое: sslip.io (если очень спешишь)

Открой `http://<IP>.sslip.io` — это уже работает, никаких настроек делать не надо. Но SSL так не получишь.

### DuckDNS + Let's Encrypt — нормальный путь

1. Регистрируешься на duckdns.org через GitHub/Google
2. Создаешь поддомен (например, `freightflow.duckdns.org`)
3. Привязываешь к IP сервера

На сервере:

```bash
sudo apt install -y certbot
sudo docker compose -f docker-compose.prod.yml stop frontend
sudo certbot certonly --standalone -d freightflow.duckdns.org
```

После получения сертификата — добавь в `docker-compose.prod.yml` монтирование сертификатов в frontend, и в `nginx.conf` добавь HTTPS-блок. Если до этого дойдешь и нужна будет помощь — спроси, дам пошагово.

Для дипломной защиты обычно достаточно просто IP-адреса, особенно если показываешь сам.

---

## 10. Полезные команды на сервере

### Просмотр логов

```bash
# Все сервисы в реальном времени
docker compose -f docker-compose.prod.yml logs -f

# Только backend
docker compose -f docker-compose.prod.yml logs -f backend

# Последние 50 строк
docker compose -f docker-compose.prod.yml logs --tail=50 backend
```

### Перезапуск отдельного сервиса

```bash
docker compose -f docker-compose.prod.yml restart backend
```

### Обновление проекта (когда что-то поменял локально)

```bash
cd ~/freight-calculator
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

Если меняли модели БД — еще:

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Полная остановка

```bash
docker compose -f docker-compose.prod.yml stop      # остановить, сохранить контейнеры и БД
docker compose -f docker-compose.prod.yml down      # остановить и удалить контейнеры (БД останется)
docker compose -f docker-compose.prod.yml down -v   # ⚠️ + удалить БД (потеря данных!)
```

### Подключение к БД

```bash
docker compose -f docker-compose.prod.yml exec postgres psql -U freight_user -d freight_db
```

### Бэкап БД

```bash
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U freight_user freight_db > backup-$(date +%Y%m%d).sql
```

### Просмотр ресурсов

```bash
docker stats                     # CPU/RAM по контейнерам
df -h                            # диск
free -h                          # память
```

---

## 11. Что делать после защиты

После защиты можно:

- **Оставить сервер** работать как портфолио (потратишь ~300₽/мес)
- **Просто удалить VPS** через панель Aeza — снимется и оплата
- **Поставить на паузу** — Aeza позволяет приостановить сервер без удаления

---

## Что делать, если что-то пошло не так

**Сайт не открывается по IP в браузере** — проверь:
1. Файрвол: `sudo ufw status` — порт 80 должен быть разрешен
2. Контейнеры: `docker compose -f docker-compose.prod.yml ps` — все Up?
3. Логи nginx: `docker compose -f docker-compose.prod.yml logs frontend`

**Бэкенд возвращает 500** — смотри логи бэкенда. Чаще всего:
- Не применены миграции — выполни `alembic upgrade head`
- Пароль БД не совпадает — пересоздай `.env` и `docker compose down -v && up -d --build`

**Карты не работают** — Nominatim/OSRM могут быть временно недоступны. Подожди или попробуй другие адреса.

**Не хватает памяти при сборке фронта** — Vite требует ~1GB RAM. Если на VPS только 1GB и крашится: создай swap-файл:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Это добавит 2GB swap, и сборка пройдет даже на минимальном тарифе.

---

## Checklist для защиты

- [ ] Сервер доступен по IP в браузере
- [ ] Лендинг открывается
- [ ] Логин работает через демо-кнопки
- [ ] Дашборд показывает графики
- [ ] Калькулятор с картой работает (попробуй пару разных адресов)
- [ ] CRUD-страницы открываются
- [ ] Можно создать заявку, назначить ТС
- [ ] Driver-аккаунт видит свои рейсы
- [ ] Swagger /docs открывается
- [ ] Тесты на сервере проходят: `docker compose -f docker-compose.prod.yml exec backend pytest`