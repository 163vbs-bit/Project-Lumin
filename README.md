# Lumin

Lumin — веб-платформа для тестирования знаний по программированию. В проекте есть роли студента и преподавателя, прохождение тестов, история попыток, статистика, категории, результаты с разбором ответов, панель преподавателя и автоматические QA-отчеты.

## Стек

- Frontend: React, Vite, TypeScript, TailwindCSS, Framer Motion, React Router, Axios, Zustand, Recharts.
- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT, bcrypt.
- Database: PostgreSQL.
- Testing: Pytest, Locust, отдельный QA runner на Python.
- Infrastructure: Docker, Docker Compose.

## Быстрый Запуск

Из корня проекта:

```powershell
docker-compose up --build
```

После запуска:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger / API docs: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/health

Backend-контейнер при старте автоматически выполняет:

1. Миграции Alembic.
2. Seed базы данных.
3. Запуск FastAPI через Uvicorn.

## Демо-Аккаунты

Студент:

```text
Логин: demo_student
Пароль: password123
```

Преподаватель:

```text
Логин: demo_teacher
Пароль: password123
```

## Остановка Проекта

Остановить контейнеры:

```powershell
docker-compose down
```

Остановить контейнеры и удалить volume базы данных:

```powershell
docker-compose down -v
```

Команда с `-v` удалит данные PostgreSQL. После следующего запуска база будет заполнена seed-данными заново.

## Структура Проекта

```text
backend/       FastAPI backend, модели, схемы, сервисы, репозитории, миграции, тесты
frontend/      React + Vite frontend
docs/          документация проекта
load-tests/    Locust-нагрузочное тестирование
qa-tests/      автоматические QA-тест-программы и генерация отчетов
reports/       сгенерированные отчеты QA runner
docker-compose.yml
.env.example
```

## Backend Локально Без Docker

Команды выполнять из папки `backend`:

```powershell
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Для локального запуска backend нужна PostgreSQL база и корректный `DATABASE_URL`.

## Frontend Локально Без Docker

Команды выполнять из папки `frontend`:

```powershell
cd frontend
npm install
npm run dev
```

Production build:

```powershell
cd frontend
npm run build
```

Preview production build:

```powershell
cd frontend
npm run preview
```

## Backend Unit / API Tests

Команды выполнять из папки `backend`:

```powershell
cd backend
pytest
```

Если `pytest` не найден:

```powershell
cd backend
pip install -r requirements.txt
pytest
```

Эти тесты проверяют:

- регистрацию и авторизацию;
- JWT-защиту;
- создание тестов преподавателем;
- прохождение тестов студентом;
- сохранение результата попытки.

## QA Runner

QA runner — это отдельная тест-программа, которая обращается к запущенному сайту и API, создает пользователей-ботов, проверяет регистрацию, вход, роли, качество тестовых данных, нагрузку и память контейнеров.

Перед запуском QA runner проект должен быть запущен:

```powershell
docker-compose up --build
```

В другом терминале из корня проекта:

```powershell
python qa-tests/run_quality_suite.py --users 10
```

Если Windows не видит команду `python`, можно запускать полным путем:

```powershell
C:\Users\vbsli\AppData\Local\Programs\Python\Python313\python.exe qa-tests\run_quality_suite.py --users 10
```

Интерактивный PowerShell-запускатель:

```powershell
.\qa-tests\run_quality_suite.ps1
```

## QA Runner: Нагрузка 1-100 Ботов

Запуск на 1 пользователя:

```powershell
python qa-tests/run_quality_suite.py --users 1
```

Запуск на 10 пользователей:

```powershell
python qa-tests/run_quality_suite.py --users 10
```

Запуск на 100 пользователей:

```powershell
python qa-tests/run_quality_suite.py --users 100
```

Серия нагрузок одной командой:

```powershell
python qa-tests/run_quality_suite.py --users 10 --load-steps 1,10,50,100
```

В этом режиме будут созданы отдельные подпапки для `1_users`, `10_users`, `50_users`, `100_users`, а общая сравнительная таблица будет лежать в `load/load_matrix.csv`.

## Что Проверяет QA Runner

### Verification

Проверяет, что система доступна и базовая структура работает:

- backend `/health`;
- OpenAPI `/openapi.json`;
- список категорий;
- список тестов;
- frontend `/`;
- открытие первого теста.

Файл отчета:

```text
reports/qa_run_.../verification/verification_checks.csv
```

### Validation

Проверяет правила регистрации, входа и ролей:

- регистрация студента;
- регистрация преподавателя;
- отклонение неправильного email;
- отклонение короткого пароля;
- отклонение неправильной роли;
- отклонение дубля email;
- отклонение дубля username;
- вход студента;
- вход преподавателя;
- доступ преподавателя к teacher-only API;
- запрет student-доступа к teacher-only API;
- отклонение входа с неправильным паролем.

Файл отчета:

```text
reports/qa_run_.../validation/validation_accounts.csv
```

### Usability

Проверяет основные маршруты и качество тестовых данных:

- frontend-страницы открываются;
- в тестах есть вопросы;
- у вопросов есть код;
- есть варианты ответов;
- есть правильные ответы;
- нет повторов вопросов;
- нет повторов ответов;
- нет битой кодировки.

Файл отчета:

```text
reports/qa_run_.../usability/usability_checks.csv
```

### Load

Запускает ботов, каждый бот выполняет сценарий:

1. Регистрация.
2. Вход.
3. Получение текущего пользователя.
4. Открытие dashboard.
5. Получение категорий.
6. Получение списка тестов.
7. Открытие теста.
8. Отправка попытки прохождения.
9. Открытие leaderboard.

Файлы отчета:

```text
reports/qa_run_.../load/load_accounts.csv
reports/qa_run_.../load/load_steps.csv
reports/qa_run_.../load/performance_summary.csv
reports/qa_run_.../load/memory_samples.csv
reports/qa_run_.../load/memory_summary.csv
reports/qa_run_.../load/load_matrix.csv
```

## Как Читать Нагрузочный Отчет

Основные поля `load_matrix.csv`:

- `users` — сколько ботов запускалось.
- `successful_scenarios` — сколько ботов полностью прошли сценарий.
- `failed_scenarios` — сколько ботов завершились с ошибкой.
- `total_seconds` — общее время теста.
- `throughput_users_per_second` — сколько пользовательских сценариев выполнялось в секунду.
- `avg_total_ms` — среднее время полного сценария одного бота.
- `p50_total_ms` — медианное время, 50% ботов быстрее этого значения.
- `p95_total_ms` — 95% ботов быстрее этого значения.
- `max_total_ms` — самый медленный сценарий.
- `max_container_memory_mib` — максимальное потребление RAM среди Docker-контейнеров.

## HTML И CSV Отчеты

После запуска QA runner создается папка:

```text
reports/qa_run_YYYYMMDD_HHMMSS_N_users
```

В корне отчета:

```text
README.md       описание конкретного запуска
summary.csv     короткая сводка OK / FAIL
report.html     HTML-отчет для открытия в браузере
```

`report.html` удобно использовать для демонстрации на защите.

## Locust Нагрузочное Тестирование

Locust-сценарий лежит в `load-tests/locustfile.py`.

Запуск:

```powershell
cd load-tests
locust -f locustfile.py --host http://localhost:8000
```

После запуска открыть:

```text
http://localhost:8089
```

Locust использует demo-аккаунт студента и проверяет:

- список тестов;
- dashboard;
- leaderboard.

## Проверка Docker Compose

Проверить конфигурацию:

```powershell
docker compose config --quiet
```

Посмотреть контейнеры:

```powershell
docker compose ps
```

Посмотреть логи:

```powershell
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

Посмотреть потребление памяти:

```powershell
docker stats
```

## Частые Проблемы

### Port is already allocated

Значит порт уже занят. Обычно это `5173`, `8000` или `5432`.

Можно остановить старые контейнеры:

```powershell
docker-compose down
```

### База не обновилась после изменений seed

Удалить volume и запустить заново:

```powershell
docker-compose down -v
docker-compose up --build
```

### QA runner показывает FAIL в load

Проверь, что проект запущен:

```powershell
docker compose ps
```

Проверь, что backend доступен:

```powershell
curl http://localhost:8000/health
```

### QA runner показывает FAIL в usability

Обычно это значит, что в базе есть тест с недостаточным количеством вопросов, дубли ответов или некорректные тестовые данные. Подробности будут в:

```text
reports/qa_run_.../usability/usability_checks.csv
```

## Краткое Описание Для Защиты

Lumin — fullstack-платформа для проверки знаний по программированию. Frontend написан на React и TypeScript, backend — на Python FastAPI, база данных — PostgreSQL. Проект запускается через Docker Compose. Реализованы JWT-авторизация, роли студента и преподавателя, прохождение тестов, результаты, статистика, панель преподавателя и автоматическая система QA-отчетов с проверкой верификации, валидации, юзабилити, нагрузки и потребления памяти.
