from sqlalchemy import delete, or_
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Achievement, Answer, Attempt, Category, Question, Role, Statistic, Test, User, UserProgress

CATEGORIES = [
    ("Python", "Синтаксис, коллекции, функции, исключения и стандартная библиотека.", "#0ea5e9"),
    ("JavaScript", "Типы, массивы, промисы, функции и асинхронность.", "#6366f1"),
    ("TypeScript", "Типы, интерфейсы, union, generics и проверка типов.", "#2563eb"),
    ("SQL", "SELECT, JOIN, GROUP BY, фильтрация, индексы и транзакции.", "#059669"),
    ("HTML/CSS", "Семантика, формы, доступность, flexbox, grid и адаптивность.", "#db2777"),
    ("React", "Компоненты, state, props, hooks, формы и эффекты.", "#0284c7"),
    ("Git", "Коммиты, ветки, merge, rebase, stash и откат изменений.", "#e11d48"),
    ("Linux", "Файлы, права доступа, процессы, пайпы и сетевые команды.", "#ca8a04"),
    ("Algorithms", "Сложность, поиск, сортировка, стек, очередь, графы и динамика.", "#7c3aed"),
    ("Databases", "Ключи, связи, индексы, транзакции, миграции и резервные копии.", "#0f766e"),
]

ACHIEVEMENTS = [
    ("first_pass", "Первый тест", "Пройден первый тест.", 50),
    ("sharp_logic", "Точная логика", "Результат 90% или выше.", 120),
    ("streak_7", "Семь попыток", "Серия из семи успешных попыток.", 220),
    ("polyglot", "Широкий профиль", "Тесты пройдены в пяти категориях.", 300),
]

MODES = ["standard", "timed", "hardcore", "random", "practice"]
DIFFICULTIES = ["easy", "medium", "hard"]
KINDS = ["single_choice", "multiple_choice", "true_false", "code", "timed"]


def ensure_roles(db: Session) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name in ["student", "teacher"]:
        role = db.query(Role).filter_by(name=name).one_or_none()
        if role is None:
            role = Role(name=name)
            db.add(role)
        roles[name] = role
    db.commit()
    return roles


def ensure_users(db: Session, roles: dict[str, Role]) -> dict[str, User]:
    demos = [
        ("student@lumin.dev", "demo_student", "student"),
        ("teacher@lumin.dev", "demo_teacher", "teacher"),
    ]
    users: dict[str, User] = {}
    for email, username, role_name in demos:
        user = db.query(User).filter_by(username=username).one_or_none()
        if user is None:
            user = User(
                email=email,
                username=username,
                hashed_password=hash_password("password123"),
                role=roles[role_name],
                avatar_url=f"https://api.dicebear.com/8.x/identicon/svg?seed={username}",
            )
            db.add(user)
        user.xp = 0
        user.level = 1
        user.streak = 0
        users[username] = user
    db.commit()
    return users


def seed_categories(db: Session) -> list[Category]:
    categories: list[Category] = []
    for name, description, color in CATEGORIES:
        category = db.query(Category).filter_by(name=name).one_or_none()
        if category is None:
            category = Category(name=name, description=description, color=color)
            db.add(category)
        else:
            category.description = description
            category.color = color
        categories.append(category)
    db.commit()
    return categories


def seed_achievements(db: Session) -> None:
    for code, title, description, xp in ACHIEVEMENTS:
        achievement = db.query(Achievement).filter_by(code=code).one_or_none()
        if achievement is None:
            db.add(Achievement(code=code, title=title, description=description, xp_reward=xp))
        else:
            achievement.title = title
            achievement.description = description
            achievement.xp_reward = xp
    db.commit()


def reset_demo_tests(db: Session, teacher: User) -> None:
    category_names = [name for name, *_ in CATEGORIES]
    conditions = []
    for name in category_names:
        conditions.append(Test.title.like(f"{name}: тест %"))
        conditions.append(Test.title.like(f"{name} Signal %"))
    demo_tests = db.query(Test).filter(Test.author_id == teacher.id, or_(*conditions)).all()
    demo_test_ids = [test.id for test in demo_tests]
    if not demo_test_ids:
        return
    affected_user_ids = [row[0] for row in db.query(Attempt.user_id).filter(Attempt.test_id.in_(demo_test_ids)).distinct().all()]
    db.execute(delete(Attempt).where(Attempt.test_id.in_(demo_test_ids)))
    if affected_user_ids:
        db.execute(delete(Statistic).where(Statistic.user_id.in_(affected_user_ids)))
        db.execute(delete(UserProgress).where(UserProgress.user_id.in_(affected_user_ids)))
    for test in demo_tests:
        db.delete(test)
    db.commit()


def code_case(category: str, test_number: int, question_number: int) -> tuple[str, str, list[str], list[str]]:
    n = test_number + question_number
    m = test_number * 2 + question_number
    case = (question_number - 1) % 10

    if category == "Python":
        cases = [
            (f"nums = [{n}, {n + 1}, {n + 2}]\nprint([x * 2 for x in nums if x % 2 == 0])", f"Будет выведен список с удвоенными четными числами: {[x * 2 for x in [n, n + 1, n + 2] if x % 2 == 0]}."),
            (f"user = {{'name': 'Ada', 'score': {m}}}\nprint(user.get('score', 0))", f"Будет выведено число {m}, потому что ключ score есть в словаре."),
            (f"items = ({n}, {n + 1}, {n + 2})\nprint(next(x for x in items if x > {n}))", f"Будет выведено {n + 1}, первое значение больше {n}."),
            (f"try:\n    result = {m} // {test_number}\nexcept ZeroDivisionError:\n    result = 0\nprint(result)", f"Будет выведено {m // test_number}, деление выполняется без ошибки."),
            (f"def add(a, b={n}):\n    return a + b\nprint(add({m}))", f"Будет выведено {m + n}, потому что используется значение b по умолчанию."),
            (f"from pathlib import Path\np = Path('logs') / 'app.txt'\nprint(p.as_posix())", "Будет выведено logs/app.txt."),
            (f"values = [{n}, {m}, {n + m}]\nprint(values[-1])", f"Будет выведено {n + m}, последний элемент списка."),
            (f"pairs = [('a', {n}), ('b', {m})]\nprint(dict(pairs)['b'])", f"Будет выведено {m}, значение по ключу b."),
            (f"text = 'python-{n}'\nprint(text.split('-')[1])", f"Будет выведена строка '{n}'."),
            (f"total = sum(range({test_number}, {test_number + 3}))\nprint(total)", f"Будет выведено {sum(range(test_number, test_number + 3))}."),
        ]
    elif category == "JavaScript":
        cases = [
            (f"const values = [{n}, {n + 1}];\nconsole.log(values.map(x => x + 1).join(','));", f"В консоль попадет строка '{n + 1},{n + 2}'."),
            (f"const user = {{ name: 'Ada', score: {m} }};\nconsole.log(user.score ?? 0);", f"В консоль попадет {m}, потому что score не null и не undefined."),
            (f"let count = {n};\ncount += {test_number};\nconsole.log(count);", f"В консоль попадет {n + test_number}."),
            (f"const names = ['Ann', 'Bob'];\nconsole.log(names.includes('Bob'));", "В консоль попадет true."),
            (f"const value = '{n}';\nconsole.log(Number(value) + 1);", f"В консоль попадет {n + 1}."),
            (f"const result = [{n}, {m}].filter(x => x > {n});\nconsole.log(result.length);", "В консоль попадет 1."),
            (f"const copy = {{ id: {n}, active: true }};\nconsole.log({{ ...copy, active: false }}.active);", "В консоль попадет false."),
            (f"const fn = (x) => x * 3;\nconsole.log(fn({test_number}));", f"В консоль попадет {test_number * 3}."),
            (f"const title = 'lumin';\nconsole.log(title.toUpperCase());", "В консоль попадет LUMIN."),
            (f"Promise.resolve({n}).then(x => console.log(x + 2));", f"После выполнения промиса в консоль попадет {n + 2}."),
        ]
    elif category == "TypeScript":
        cases = [
            (f"type User = {{ id: number; name: string }};\nconst user: User = {{ id: {n}, name: 'Ada' }};", "Код типизируется корректно: id число, name строка."),
            (f"let value: string | number = {m};\nif (typeof value === 'number') {{ value.toFixed(0); }}", "После проверки typeof TypeScript понимает, что value является number."),
            (f"function first<T>(items: T[]): T {{ return items[0]; }}\nconst item = first<number>([{n}, {m}]);", "Generic T будет number, поэтому item имеет тип number."),
            (f"interface Point {{ x: number; y: number }}\nconst p: Point = {{ x: {n}, y: {m} }};", "Объект соответствует интерфейсу Point."),
            (f"type Status = 'draft' | 'done';\nconst status: Status = 'done';", "Значение 'done' допустимо для union-типа Status."),
            (f"const ids: readonly number[] = [{n}, {m}];\nconsole.log(ids[0]);", "Чтение из readonly массива разрешено."),
            (f"const scores: Record<string, number> = {{ math: {n} }};\nconsole.log(scores.math);", f"Record<string, number> разрешает ключ math со значением {n}."),
            (f"type User = {{ name: string; age: number }};\nconst patch: Partial<User> = {{ age: {m} }};", "Partial<User> делает поля необязательными."),
            (f"let input: unknown = 'ok';\nif (typeof input === 'string') {{ input.toUpperCase(); }}", "Метод toUpperCase доступен после narrowing до string."),
            (f"const tuple: [string, number] = ['id', {n}];\nconsole.log(tuple[1]);", f"Второй элемент tuple имеет тип number и значение {n}."),
        ]
    elif category == "SQL":
        cases = [
            ("SELECT name FROM users WHERE active = true;", "Запрос вернет имена активных пользователей."),
            ("SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;", "Запрос посчитает сотрудников по каждому department_id."),
            ("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5;", "Запрос вернет пять последних заказов по created_at."),
            ("SELECT u.name, p.title FROM users u INNER JOIN posts p ON p.user_id = u.id;", "INNER JOIN вернет только пары пользователей и постов, где есть совпадение."),
            ("SELECT name FROM products WHERE price BETWEEN 100 AND 200;", "Запрос выберет продукты с ценой от 100 до 200 включительно."),
            ("SELECT status, COUNT(*) FROM orders GROUP BY status HAVING COUNT(*) > 10;", "HAVING фильтрует группы, где заказов больше 10."),
            ("CREATE INDEX idx_users_email ON users(email);", "Команда создает индекс по колонке email."),
            ("BEGIN;\nUPDATE accounts SET balance = balance - 100 WHERE id = 1;\nCOMMIT;", "Изменение баланса фиксируется после COMMIT."),
            ("SELECT COALESCE(phone, 'не указан') FROM users;", "COALESCE подставит 'не указан', если phone равен NULL."),
            ("DELETE FROM sessions WHERE expires_at < NOW();", "Запрос удалит просроченные сессии."),
        ]
    elif category == "HTML/CSS":
        cases = [
            ('<label for="email">Email</label>\n<input id="email" type="email" required />', "label связан с input через for и id, поле становится доступнее."),
            ('<button type="submit">Сохранить</button>', "Кнопка отправит форму, потому указан type submit."),
            ('<img src="logo.png" alt="Логотип Lumin" />', "alt описывает изображение для доступности."),
            ('.card { display: flex; gap: 16px; }', "Элементы внутри .card будут расположены flex-контейнером с промежутком 16px."),
            ('.grid { display: grid; grid-template-columns: repeat(3, 1fr); }', "Контейнер получит три равные колонки."),
            ('@media (max-width: 600px) { .menu { display: none; } }', "На ширине до 600px элемент .menu будет скрыт."),
            ('<header><nav>...</nav></header>', "header и nav задают семантическую структуру страницы."),
            ('input:focus { outline: 2px solid #0ea5e9; }', "Правило делает фокус видимым для клавиатурной навигации."),
            ('.box { box-sizing: border-box; width: 200px; padding: 20px; }', "padding входит в ширину 200px благодаря border-box."),
            ('<main id="content">...</main>', "main обозначает основное содержимое страницы."),
        ]
    elif category == "React":
        cases = [
            ("const [count, setCount] = useState(0);\nsetCount(value => value + 1);", "Функциональное обновление увеличит count на 1."),
            ("useEffect(() => {\n  document.title = title;\n}, [title]);", "Эффект выполнится при изменении title."),
            ("function UserName({ name }) {\n  return <span>{name}</span>;\n}", "Компонент выводит значение prop name."),
            ("<input value={email} onChange={e => setEmail(e.target.value)} />", "Это контролируемый input, значение хранится в state."),
            ("items.map(item => <li key={item.id}>{item.name}</li>)", "key помогает React сопоставлять элементы списка."),
            ("const visible = isOpen ? <Panel /> : null;", "Panel будет отрисован только когда isOpen истинно."),
            ("const value = useMemo(() => heavy(items), [items]);", "useMemo пересчитает value при изменении items."),
            ("const navigate = useNavigate();\nnavigate('/dashboard');", "Код программно перейдет на маршрут /dashboard."),
            ("const ThemeContext = createContext('dark');", "Создается контекст со значением по умолчанию 'dark'."),
            ("function useToggle() {\n  const [on, setOn] = useState(false);\n  return [on, () => setOn(v => !v)];\n}", "Это пользовательский hook для переключения boolean-состояния."),
        ]
    elif category == "Git":
        cases = [
            ("git checkout -b feature/tests", "Команда создаст и сразу выберет ветку feature/tests."),
            ("git status", "Команда покажет состояние рабочей директории и индекса."),
            ("git add app.py\ngit commit -m \"add app\"", "Файл app.py попадет в коммит с сообщением add app."),
            ("git merge feature/auth", "Текущая ветка попытается принять изменения из feature/auth."),
            ("git rebase main", "Коммиты текущей ветки будут перенесены поверх main."),
            ("git stash push -m \"wip\"", "Незавершенные изменения будут временно сохранены в stash."),
            ("git revert HEAD", "Будет создан новый коммит, отменяющий изменения последнего коммита."),
            ("git tag v1.0.0", "Будет создан тег v1.0.0 на текущем коммите."),
            ("git remote -v", "Команда покажет подключенные удаленные репозитории."),
            ("git log --oneline -3", "Команда покажет три последних коммита в кратком виде."),
        ]
    elif category == "Linux":
        cases = [
            ("chmod 640 report.txt", "Владелец получит чтение и запись, группа чтение, остальные без доступа."),
            ("printf 'api\\nweb\\n' | grep api", "Команда выведет строку api."),
            ("ps aux | grep nginx", "Команда поможет найти процессы, связанные с nginx."),
            ("kill -15 1234", "Процессу 1234 будет отправлен сигнал SIGTERM."),
            ("tar -czf logs.tar.gz logs/", "Папка logs будет упакована в gzip-архив."),
            ("curl -I https://example.com", "Команда запросит только HTTP-заголовки."),
            ("systemctl status postgresql", "Команда покажет статус сервиса postgresql."),
            ("journalctl -u nginx --since today", "Команда покажет сегодняшние логи сервиса nginx."),
            ("find . -name '*.py'", "Команда найдет Python-файлы ниже текущей директории."),
            ("ssh user@server", "Команда откроет SSH-подключение к server от имени user."),
        ]
    elif category == "Algorithms":
        cases = [
            ("for i in range(n):\n    for j in range(n):\n        total += 1", "Сложность фрагмента O(n^2)."),
            ("left, right = 0, len(nums) - 1\nwhile left <= right:\n    mid = (left + right) // 2", "Это основа бинарного поиска."),
            ("seen = set()\nfor x in nums:\n    if x in seen: return True\n    seen.add(x)", "Код проверяет наличие повторов за O(n) в среднем."),
            ("stack.append(value)\nlast = stack.pop()", "Это поведение стека LIFO."),
            ("queue.append(value)\nfirst = queue.pop(0)", "Это поведение очереди FIFO."),
            ("def dfs(v):\n    visited.add(v)\n    for to in graph[v]: dfs(to)", "Функция выполняет обход графа в глубину."),
            ("while heap:\n    value = heappop(heap)", "Из heap извлекаются элементы по приоритету."),
            ("dp[i] = max(dp[i - 1], dp[i - 2] + value)", "Это переход динамического программирования."),
            ("nums.sort()\nprint(nums[0])", "После сортировки nums[0] содержит минимальный элемент."),
            ("slow = fast = head\nfast = fast.next.next\nslow = slow.next", "Это схема двух указателей с разной скоростью."),
        ]
    else:
        cases = [
            ("CREATE TABLE users (id INT PRIMARY KEY, email TEXT UNIQUE);", "id является первичным ключом, email должен быть уникальным."),
            ("ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id);", "Внешний ключ связывает orders.user_id с users.id."),
            ("CREATE INDEX idx_orders_created_at ON orders(created_at);", "Индекс ускоряет поиск и сортировку по created_at."),
            ("BEGIN;\nUPDATE products SET stock = stock - 1 WHERE id = 10;\nCOMMIT;", "Обновление выполняется внутри транзакции."),
            ("SELECT * FROM users WHERE email = 'a@b.com';", "При индексе по email такой поиск обычно быстрее."),
            ("ALTER TABLE users ADD COLUMN last_login TIMESTAMP;", "Миграция добавляет колонку last_login."),
            ("BACKUP DATABASE app TO DISK = 'app.bak';", "Команда создает резервную копию базы."),
            ("SELECT * FROM orders WHERE user_id = 5;", "Запрос выбирает заказы конкретного пользователя."),
            ("ROLLBACK;", "ROLLBACK отменяет изменения текущей транзакции."),
            ("EXPLAIN SELECT * FROM users WHERE id = 1;", "EXPLAIN покажет план выполнения запроса."),
        ]

    code, correct = cases[case]
    if category in {"Python", "JavaScript", "TypeScript", "React", "Algorithms"}:
        wrong = [
            "Фрагмент завершится синтаксической ошибкой до выполнения.",
            "Результатом будет пустое значение, потому что последняя строка не выполнится.",
            "Фрагмент изменит исходные данные, хотя в коде нет такой операции.",
        ]
    elif category in {"SQL", "Databases"}:
        wrong = [
            "Запрос удалит все строки таблицы.",
            "Команда создаст новую таблицу вместо выполнения показанной операции.",
            "Условие или ключевое слово в запросе не влияет на результат.",
        ]
    elif category == "HTML/CSS":
        wrong = [
            "Браузер полностью проигнорирует этот фрагмент разметки.",
            "Фрагмент удалит элемент из DOM без JavaScript.",
            "Этот код отключит доступность элемента для всех пользователей.",
        ]
    elif category == "Git":
        wrong = [
            "Команда удалит всю историю репозитория.",
            "Команда автоматически отправит изменения на удаленный сервер.",
            "Команда создаст новый коммит без участия пользователя.",
        ]
    else:
        wrong = [
            "Команда удалит все файлы в текущей директории.",
            "Команда изменит права доступа всех пользователей системы.",
            "Команда выполнится справа налево, потому что используется shell.",
        ]
    return code, correct, wrong, [f"Фрагмент относится к теме {category}.", "Ответ определяется показанными строками.", "Важно учитывать аргументы команды или выражения."]


def build_answers(category: str, kind: str, test_number: int, question_number: int) -> tuple[str, str, list[Answer]]:
    code, correct, wrong, facts = code_case(category, test_number, question_number)
    marker = f" ({category}, вариант {test_number}.{question_number})"
    if kind == "multiple_choice":
        answers = [
            Answer(body=f"{correct}{marker}", is_correct=True),
            Answer(body=f"{wrong[0]}{marker}", is_correct=False),
            Answer(body=f"{facts[0]}{marker}", is_correct=True),
            Answer(body=f"{wrong[1]}{marker}", is_correct=False),
        ]
        body = "Выберите все верные утверждения о фрагменте."
    elif kind == "true_false":
        answers = [
            Answer(body=f"Верно: {correct}{marker}", is_correct=True),
            Answer(body=f"Неверно: {wrong[0]}{marker}", is_correct=False),
        ]
        body = f"Верно ли, что этот фрагмент работает так: {correct}"
    else:
        answers = [Answer(body=f"{correct}{marker}", is_correct=True)] + [Answer(body=f"{text}{marker}", is_correct=False) for text in wrong]
        body = "Что произойдет при выполнении этого фрагмента?"
    return body, code, answers


def seed_tests(db: Session, categories: list[Category], teacher: User) -> None:
    reset_demo_tests(db, teacher)
    for category_index, category in enumerate(categories):
        for test_number in range(1, 6):
            test = Test(
                title=f"{category.name}: тест {test_number}",
                description=f"Практический тест по теме {category.name}: каждый вопрос связан с конкретным фрагментом.",
                difficulty=DIFFICULTIES[(category_index + test_number) % len(DIFFICULTIES)],
                mode=MODES[(category_index + test_number) % len(MODES)],
                time_limit_seconds=900 if test_number % 2 == 0 else None,
                category=category,
                author=teacher,
            )
            for question_number in range(1, 11):
                kind = KINDS[(question_number + test_number + category_index) % len(KINDS)]
                body, code, answers = build_answers(category.name, kind, test_number, question_number)
                test.questions.append(
                    Question(
                        body=f"{category.name}: вариант {test_number}.{question_number}. {body}",
                        kind=kind,
                        code_snippet=code,
                        time_limit_seconds=45 if kind == "timed" else None,
                        points=10 + (question_number % 3) * 5,
                        position=question_number,
                        answers=answers,
                    )
                )
            db.add(test)
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        roles = ensure_roles(db)
        users = ensure_users(db, roles)
        categories = seed_categories(db)
        seed_achievements(db)
        seed_tests(db, categories, users["demo_teacher"])
        print("Seed complete: demo tests rebuilt with concrete code-based questions.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
