from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import statistics
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

QA_EMAIL_DOMAIN = "luminqa.dev"


@dataclass
class HttpResult:
    method: str
    url: str
    status: int
    ok: bool
    elapsed_ms: float
    data: Any
    error: str = ""


def request_json(method: str, url: str, token: str | None = None, payload: Any | None = None, timeout: float = 10) -> HttpResult:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    started = time.perf_counter()
    try:
        req = Request(url, data=body, headers=headers, method=method)
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            elapsed = (time.perf_counter() - started) * 1000
            data = json.loads(raw) if raw else None
            status = response.status
            return HttpResult(method, url, status, 200 <= status < 300, elapsed, data)
    except HTTPError as exc:
        elapsed = (time.perf_counter() - started) * 1000
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw else None
            error = data.get("detail", raw) if isinstance(data, dict) else raw
        except json.JSONDecodeError:
            data = None
            error = raw
        return HttpResult(method, url, exc.code, False, elapsed, data, str(error))
    except (URLError, TimeoutError, OSError) as exc:
        elapsed = (time.perf_counter() - started) * 1000
        return HttpResult(method, url, 0, False, elapsed, None, str(exc))


def request_text(method: str, url: str, timeout: float = 10) -> HttpResult:
    started = time.perf_counter()
    try:
        req = Request(url, headers={"Accept": "text/html,*/*"}, method=method)
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            elapsed = (time.perf_counter() - started) * 1000
            return HttpResult(method, url, response.status, 200 <= response.status < 300, elapsed, raw)
    except HTTPError as exc:
        elapsed = (time.perf_counter() - started) * 1000
        raw = exc.read().decode("utf-8", errors="replace")
        return HttpResult(method, url, exc.code, False, elapsed, raw, raw[:300])
    except (URLError, TimeoutError, OSError) as exc:
        elapsed = (time.perf_counter() - started) * 1000
        return HttpResult(method, url, 0, False, elapsed, "", str(exc))


def api_url(base_url: str, path: str, **query: Any) -> str:
    url = f"{base_url.rstrip('/')}{path}"
    clean_query = {key: value for key, value in query.items() if value is not None}
    if clean_query:
        url = f"{url}?{urlencode(clean_query)}"
    return url


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row.keys():
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]), encoding="utf-8")


def write_html_report(path: Path, title: str, sections: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for section in sections:
        rows = section.get("rows", [])
        if not rows:
            table = "<p>Нет данных.</p>"
        else:
            columns = list(rows[0].keys())
            head = "".join(f"<th>{html.escape(str(column))}</th>" for column in columns)
            body = []
            for row in rows:
                cells = "".join(f"<td>{html.escape(str(row.get(column, '')))}</td>" for column in columns)
                body.append(f"<tr>{cells}</tr>")
            table = f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"
        blocks.append(f"<section><h2>{html.escape(section['title'])}</h2>{table}</section>")
    path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"ru\">",
                "<head>",
                "<meta charset=\"utf-8\">",
                f"<title>{html.escape(title)}</title>",
                "<style>",
                "body{margin:0;background:#f5f7fb;color:#172033;font:14px/1.5 Inter,Arial,sans-serif}",
                "main{max-width:1180px;margin:0 auto;padding:32px}",
                "h1{font-size:28px;margin:0 0 20px}",
                "h2{font-size:18px;margin:28px 0 12px}",
                "section{background:#fff;border:1px solid #dbe3ef;border-radius:12px;padding:18px;margin:16px 0;box-shadow:0 8px 24px rgba(23,32,51,.06)}",
                "table{width:100%;border-collapse:collapse;overflow:hidden;border-radius:10px}",
                "th,td{padding:10px 12px;border-bottom:1px solid #e7edf6;text-align:left;vertical-align:top}",
                "th{background:#edf3fb;color:#4b5f7d;font-size:12px;text-transform:uppercase;letter-spacing:.04em}",
                "tr:last-child td{border-bottom:0}",
                "</style>",
                "</head>",
                "<body>",
                "<main>",
                f"<h1>{html.escape(title)}</h1>",
                *blocks,
                "</main>",
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil((p / 100) * len(ordered)) - 1))
    return ordered[index]


def status(ok: bool) -> str:
    return "OK" if ok else "FAIL"


def run_verification(base_url: str, frontend_url: str, out_dir: Path, timeout: float) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    checks = [
        ("backend health", request_json("GET", api_url(base_url, "/health"), timeout=timeout), lambda r: r.ok and r.data.get("status") == "ok"),
        ("openapi schema", request_json("GET", api_url(base_url, "/openapi.json"), timeout=timeout), lambda r: r.ok and "paths" in r.data),
        ("categories", request_json("GET", api_url(base_url, "/api/tests/categories"), timeout=timeout), lambda r: r.ok and len(r.data) >= 10),
        ("tests list", request_json("GET", api_url(base_url, "/api/tests", limit=100), timeout=timeout), lambda r: r.ok and len(r.data) >= 50),
        ("frontend root", request_text("GET", frontend_url.rstrip("/") + "/", timeout=timeout), lambda r: r.ok and "root" in str(r.data)),
    ]

    tests_result = checks[3][1]
    if tests_result.ok and tests_result.data:
        first_id = tests_result.data[0]["id"]
        detail = request_json("GET", api_url(base_url, f"/api/tests/{first_id}"), timeout=timeout)
        checks.append(("first test detail", detail, lambda r: r.ok and len(r.data.get("questions", [])) >= 10))

    for name, result, predicate in checks:
        passed = False
        try:
            passed = predicate(result)
        except Exception as exc:
            result.error = str(exc)
        rows.append(
            {
                "check": name,
                "status": status(passed),
                "http_status": result.status,
                "elapsed_ms": round(result.elapsed_ms, 2),
                "details": result.error or "Проверка пройдена",
            }
        )

    write_csv(out_dir / "verification" / "verification_checks.csv", rows)
    write_markdown(
        out_dir / "verification" / "README.md",
        "Верификация",
        [
            "Проверяется доступность корня frontend, backend healthcheck, OpenAPI, категории и тесты.",
            "",
            f"- Всего проверок: {len(rows)}",
            f"- Успешно: {sum(1 for row in rows if row['status'] == 'OK')}",
            f"- Ошибок: {sum(1 for row in rows if row['status'] != 'OK')}",
            "",
            "Подробная таблица: `verification_checks.csv`.",
        ],
    )
    return {"rows": rows}


def run_validation(base_url: str, out_dir: Path, run_id: str, timeout: float) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    valid_user = {
        "email": f"qa_valid_{run_id}@{QA_EMAIL_DOMAIN}",
        "username": f"qa_valid_{run_id}",
        "password": "password123",
        "role": "student",
    }
    teacher_user = {
        "email": f"qa_teacher_{run_id}@{QA_EMAIL_DOMAIN}",
        "username": f"qa_teacher_{run_id}",
        "password": "password123",
        "role": "teacher",
    }

    cases = [
        ("valid_registration", valid_user, True),
        ("valid_teacher_registration", teacher_user, True),
        ("bad_email", {**valid_user, "email": "bad-email", "username": f"qa_bad_email_{run_id}"}, False),
        ("short_password", {**valid_user, "email": f"qa_short_{run_id}@{QA_EMAIL_DOMAIN}", "username": f"qa_short_{run_id}", "password": "123"}, False),
        ("bad_role", {**valid_user, "email": f"qa_role_{run_id}@{QA_EMAIL_DOMAIN}", "username": f"qa_role_{run_id}", "role": "admin"}, False),
        ("duplicate_email", {**valid_user, "username": f"qa_dup_email_{run_id}"}, False),
        ("duplicate_username", {**valid_user, "email": f"qa_dup_user_{run_id}@{QA_EMAIL_DOMAIN}"}, False),
    ]

    created_valid_user = False
    created_teacher_user = False
    for case_name, payload, should_pass in cases:
        result = request_json("POST", api_url(base_url, "/api/auth/register"), payload=payload, timeout=timeout)
        actual_pass = result.status in {200, 201}
        if case_name == "valid_registration" and actual_pass:
            created_valid_user = True
        if case_name == "valid_teacher_registration" and actual_pass:
            created_teacher_user = True
        rows.append(
            {
                "case": case_name,
                "username": payload["username"],
                "email": payload["email"],
                "role": payload["role"],
                "expected": "SUCCESS" if should_pass else "REJECT",
                "actual": "SUCCESS" if actual_pass else "REJECT",
                "status": status(actual_pass == should_pass),
                "http_status": result.status,
                "message": result.error or "ok",
                "elapsed_ms": round(result.elapsed_ms, 2),
            }
        )

    login_ok = request_json("POST", api_url(base_url, "/api/auth/login"), payload={"username": valid_user["username"], "password": valid_user["password"]}, timeout=timeout)
    student_token = login_ok.data.get("access_token") if login_ok.ok and isinstance(login_ok.data, dict) else None
    rows.append(
        {
            "case": "login_valid_user",
            "username": valid_user["username"],
            "email": valid_user["email"],
            "role": valid_user["role"],
            "expected": "SUCCESS",
            "actual": "SUCCESS" if login_ok.ok else "REJECT",
            "status": status(created_valid_user and login_ok.ok),
            "http_status": login_ok.status,
            "message": login_ok.error or "ok",
            "elapsed_ms": round(login_ok.elapsed_ms, 2),
        }
    )

    teacher_login = request_json("POST", api_url(base_url, "/api/auth/login"), payload={"username": teacher_user["username"], "password": teacher_user["password"]}, timeout=timeout)
    teacher_token = teacher_login.data.get("access_token") if teacher_login.ok and isinstance(teacher_login.data, dict) else None
    rows.append(
        {
            "case": "login_valid_teacher",
            "username": teacher_user["username"],
            "email": teacher_user["email"],
            "role": teacher_user["role"],
            "expected": "SUCCESS",
            "actual": "SUCCESS" if teacher_login.ok else "REJECT",
            "status": status(created_teacher_user and teacher_login.ok),
            "http_status": teacher_login.status,
            "message": teacher_login.error or "ok",
            "elapsed_ms": round(teacher_login.elapsed_ms, 2),
        }
    )

    teacher_analytics = request_json("GET", api_url(base_url, "/api/analytics/teacher"), token=teacher_token, timeout=timeout)
    rows.append(
        {
            "case": "teacher_analytics_allowed",
            "username": teacher_user["username"],
            "email": teacher_user["email"],
            "role": teacher_user["role"],
            "expected": "SUCCESS",
            "actual": "SUCCESS" if teacher_analytics.ok else "REJECT",
            "status": status(bool(teacher_token) and teacher_analytics.ok),
            "http_status": teacher_analytics.status,
            "message": teacher_analytics.error or "ok",
            "elapsed_ms": round(teacher_analytics.elapsed_ms, 2),
        }
    )

    student_teacher_analytics = request_json("GET", api_url(base_url, "/api/analytics/teacher"), token=student_token, timeout=timeout)
    rows.append(
        {
            "case": "student_teacher_analytics_forbidden",
            "username": valid_user["username"],
            "email": valid_user["email"],
            "role": valid_user["role"],
            "expected": "REJECT",
            "actual": "SUCCESS" if student_teacher_analytics.ok else "REJECT",
            "status": status(not student_teacher_analytics.ok and student_teacher_analytics.status in {401, 403}),
            "http_status": student_teacher_analytics.status,
            "message": student_teacher_analytics.error or "ok",
            "elapsed_ms": round(student_teacher_analytics.elapsed_ms, 2),
        }
    )

    login_bad = request_json("POST", api_url(base_url, "/api/auth/login"), payload={"username": valid_user["username"], "password": "wrong-password"}, timeout=timeout)
    rows.append(
        {
            "case": "login_wrong_password",
            "username": valid_user["username"],
            "email": valid_user["email"],
            "role": valid_user["role"],
            "expected": "REJECT",
            "actual": "SUCCESS" if login_bad.ok else "REJECT",
            "status": status(not login_bad.ok),
            "http_status": login_bad.status,
            "message": login_bad.error or "ok",
            "elapsed_ms": round(login_bad.elapsed_ms, 2),
        }
    )

    write_csv(out_dir / "validation" / "validation_accounts.csv", rows)
    write_markdown(
        out_dir / "validation" / "README.md",
        "Валидация",
        [
            "Проверяются правила регистрации и входа: корректный аккаунт, неправильная почта, короткий пароль, неверная роль, дубли почты/логина и неверный пароль.",
            "",
            f"- Всего кейсов: {len(rows)}",
            f"- Успешно пройдено: {sum(1 for row in rows if row['status'] == 'OK')}",
            f"- Провалено: {sum(1 for row in rows if row['status'] != 'OK')}",
            "",
            "Подробная таблица: `validation_accounts.csv`.",
        ],
    )
    return {"rows": rows, "valid_user": valid_user}


def inspect_test_quality(base_url: str, timeout: float) -> list[dict[str, Any]]:
    list_result = request_json("GET", api_url(base_url, "/api/tests", limit=100), timeout=timeout)
    if not list_result.ok:
        return [{"scope": "tests", "status": "FAIL", "details": list_result.error or "Не удалось получить список тестов"}]

    rows: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    seen_answers: set[str] = set()
    mojibake_pattern = re.compile(r"Рџ|РЎ|Рё|Рґ|Рµ|СЃ|С‚|В·|В«|В»")
    for item in list_result.data:
        detail = request_json("GET", api_url(base_url, f"/api/tests/{item['id']}"), timeout=timeout)
        if not detail.ok:
            rows.append({"scope": item["title"], "status": "FAIL", "details": detail.error})
            continue
        questions = detail.data.get("questions", [])
        if len(questions) < 10:
            rows.append({"scope": item["title"], "status": "FAIL", "details": f"В тесте меньше 10 вопросов: {len(questions)}"})
        for question in questions:
            answers = question.get("answers", [])
            correct_count = sum(1 for answer in answers if answer.get("is_correct"))
            problems: list[str] = []
            if not question.get("code_snippet"):
                problems.append("нет фрагмента кода")
            if len(answers) < 2:
                problems.append("меньше двух ответов")
            if correct_count < 1:
                problems.append("нет правильного ответа")
            if question["kind"] != "multiple_choice" and correct_count != 1:
                problems.append("для одиночного вопроса должен быть один правильный ответ")
            if question["body"] in seen_questions:
                problems.append("повтор вопроса")
            seen_questions.add(question["body"])
            if mojibake_pattern.search(question["body"]):
                problems.append("битая кодировка в вопросе")
            for answer in answers:
                if answer["body"] in seen_answers:
                    problems.append("повтор ответа")
                seen_answers.add(answer["body"])
                if mojibake_pattern.search(answer["body"]):
                    problems.append("битая кодировка в ответе")
            rows.append(
                {
                    "scope": f"{item['title']} / вопрос {question.get('position')}",
                    "status": "FAIL" if problems else "OK",
                    "details": "; ".join(problems) if problems else "Вопрос корректен",
                }
            )
    return rows


def run_usability(base_url: str, frontend_url: str, out_dir: Path, timeout: float) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    routes = ["/", "/dashboard", "/categories", "/leaderboard", "/profile"]
    for route in routes:
        result = request_text("GET", frontend_url.rstrip("/") + route, timeout=timeout)
        rows.append(
            {
                "scope": f"frontend {route}",
                "status": status(result.ok),
                "details": result.error or f"HTTP {result.status}",
                "elapsed_ms": round(result.elapsed_ms, 2),
            }
        )

    quality_rows = inspect_test_quality(base_url, timeout)
    for row in quality_rows:
        row.setdefault("elapsed_ms", "")
    rows.extend(quality_rows)

    write_csv(out_dir / "usability" / "usability_checks.csv", rows)
    write_markdown(
        out_dir / "usability" / "README.md",
        "Юзабилити и качество данных",
        [
            "Проверяются frontend-маршруты и качество тестовых данных: наличие кода, правильных ответов, отсутствие дублей и битой кодировки.",
            "",
            f"- Всего проверок: {len(rows)}",
            f"- Успешно: {sum(1 for row in rows if row['status'] == 'OK')}",
            f"- Ошибок: {sum(1 for row in rows if row['status'] != 'OK')}",
            "",
            "Подробная таблица: `usability_checks.csv`.",
        ],
    )
    return {"rows": rows}


def docker_stats_sample() -> list[dict[str, Any]]:
    try:
        completed = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{json .}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if completed.returncode != 0:
        return []
    samples: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        samples.append(
            {
                "container": item.get("Name", ""),
                "cpu_percent": item.get("CPUPerc", ""),
                "memory_usage": item.get("MemUsage", ""),
                "memory_mib": parse_memory_mib(item.get("MemUsage", "")),
                "net_io": item.get("NetIO", ""),
                "block_io": item.get("BlockIO", ""),
            }
        )
    return samples


def parse_memory_mib(value: str) -> float:
    match = re.match(r"\s*([0-9.]+)\s*([KMG]i?B)", value)
    if not match:
        return 0
    amount = float(match.group(1))
    unit = match.group(2)
    if unit in {"KiB", "KB"}:
        return amount / 1024
    if unit in {"GiB", "GB"}:
        return amount * 1024
    return amount


def bot_flow(base_url: str, run_id: str, index: int, timeout: float) -> dict[str, Any]:
    username = f"qa_bot_{run_id}_{index:03d}"
    email = f"{username}@{QA_EMAIL_DOMAIN}"
    password = "password123"
    started = time.perf_counter()
    steps: list[dict[str, Any]] = []

    def step(name: str, result: HttpResult) -> HttpResult:
        steps.append({"name": name, "status": result.status, "ok": result.ok, "elapsed_ms": result.elapsed_ms, "error": result.error})
        return result

    register = step("register", request_json("POST", api_url(base_url, "/api/auth/register"), payload={"email": email, "username": username, "password": password, "role": "student"}, timeout=timeout))
    login = step("login", request_json("POST", api_url(base_url, "/api/auth/login"), payload={"username": username, "password": password}, timeout=timeout))
    token = login.data.get("access_token") if login.ok and isinstance(login.data, dict) else None

    if token:
        step("me", request_json("GET", api_url(base_url, "/api/auth/me"), token=token, timeout=timeout))
        step("dashboard", request_json("GET", api_url(base_url, "/api/analytics/dashboard"), token=token, timeout=timeout))
        step("categories", request_json("GET", api_url(base_url, "/api/tests/categories"), token=token, timeout=timeout))
        tests = step("tests", request_json("GET", api_url(base_url, "/api/tests", limit=10), token=token, timeout=timeout))
        if tests.ok and tests.data:
            test_id = tests.data[index % len(tests.data)]["id"]
            detail = step("test_detail", request_json("GET", api_url(base_url, f"/api/tests/{test_id}"), token=token, timeout=timeout))
            if detail.ok:
                answers_payload = {}
                for question in detail.data.get("questions", []):
                    correct_ids = [answer["id"] for answer in question.get("answers", []) if answer.get("is_correct")]
                    answers_payload[str(question["id"])] = correct_ids[:1]
                step("attempt", request_json("POST", api_url(base_url, f"/api/tests/{test_id}/attempts"), token=token, payload={"answers": answers_payload, "duration_seconds": 15, "mode": detail.data.get("mode", "standard")}, timeout=timeout))
        step("leaderboard", request_json("GET", api_url(base_url, "/api/users/leaderboard"), token=token, timeout=timeout))

    elapsed_total = (time.perf_counter() - started) * 1000
    ok = bool(steps) and all(item["ok"] for item in steps)
    return {
        "bot_index": index,
        "username": username,
        "email": email,
        "registered": register.ok,
        "login": login.ok,
        "scenario_ok": ok,
        "steps": len(steps),
        "total_ms": round(elapsed_total, 2),
        "avg_step_ms": round(statistics.mean([item["elapsed_ms"] for item in steps]), 2) if steps else 0,
        "errors": " | ".join(f"{item['name']}: {item['error'] or item['status']}" for item in steps if not item["ok"]),
        "step_rows": steps,
    }


def run_load(base_url: str, out_dir: Path, users: int, run_id: str, timeout: float, section_name: str = "") -> dict[str, Any]:
    users = max(1, min(100, users))
    load_dir = out_dir / "load" / section_name if section_name else out_dir / "load"
    memory_rows: list[dict[str, Any]] = []
    stop_sampling = threading.Event()

    def collect_memory_sample() -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        for sample in docker_stats_sample():
            memory_rows.append({"timestamp": timestamp, **sample})

    def sampler() -> None:
        while not stop_sampling.is_set():
            collect_memory_sample()
            time.sleep(0.75)

    collect_memory_sample()
    sampling_thread = threading.Thread(target=sampler, daemon=True)
    sampling_thread.start()
    started = time.perf_counter()
    bot_rows: list[dict[str, Any]] = []
    step_rows: list[dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=min(users, 25)) as executor:
        futures = [executor.submit(bot_flow, base_url, run_id, index, timeout) for index in range(1, users + 1)]
        for future in as_completed(futures):
            result = future.result()
            step_rows.extend({"bot_index": result["bot_index"], "username": result["username"], **step} for step in result.pop("step_rows"))
            bot_rows.append(result)

    stop_sampling.set()
    sampling_thread.join(timeout=2)
    collect_memory_sample()
    total_seconds = time.perf_counter() - started
    total_times = [row["total_ms"] for row in bot_rows]
    successful = sum(1 for row in bot_rows if row["scenario_ok"])
    summary_rows = [
        {
            "users": users,
            "successful_scenarios": successful,
            "failed_scenarios": users - successful,
            "total_seconds": round(total_seconds, 2),
            "throughput_users_per_second": round(users / total_seconds, 2) if total_seconds else 0,
            "avg_total_ms": round(statistics.mean(total_times), 2) if total_times else 0,
            "p50_total_ms": round(percentile(total_times, 50), 2),
            "p95_total_ms": round(percentile(total_times, 95), 2),
            "max_total_ms": round(max(total_times), 2) if total_times else 0,
        }
    ]

    memory_summary: list[dict[str, Any]] = []
    by_container: dict[str, list[float]] = {}
    for row in memory_rows:
        by_container.setdefault(row["container"], []).append(float(row["memory_mib"] or 0))
    for container, values in by_container.items():
        memory_summary.append(
            {
                "container": container,
                "samples": len(values),
                "avg_memory_mib": round(statistics.mean(values), 2) if values else 0,
                "max_memory_mib": round(max(values), 2) if values else 0,
            }
        )
    if not memory_summary:
        memory_summary.append(
            {
                "container": "docker_stats_unavailable",
                "samples": 0,
                "avg_memory_mib": 0,
                "max_memory_mib": 0,
            }
        )

    write_csv(load_dir / "load_accounts.csv", sorted(bot_rows, key=lambda row: row["bot_index"]))
    write_csv(load_dir / "load_steps.csv", sorted(step_rows, key=lambda row: (row["bot_index"], row["name"])))
    write_csv(load_dir / "performance_summary.csv", summary_rows)
    write_csv(
        load_dir / "memory_samples.csv",
        memory_rows,
        ["timestamp", "container", "cpu_percent", "memory_usage", "memory_mib", "net_io", "block_io"],
    )
    write_csv(load_dir / "memory_summary.csv", memory_summary, ["container", "samples", "avg_memory_mib", "max_memory_mib"])
    write_markdown(
        load_dir / "README.md",
        "Нагрузочное тестирование",
        [
            f"Сценарий: {users} ботов одновременно регистрируются, входят, открывают API, получают тест и отправляют попытку.",
            "",
            f"- Успешных сценариев: {successful}",
            f"- Ошибок сценариев: {users - successful}",
            f"- Общее время: {summary_rows[0]['total_seconds']} сек.",
            f"- P95 полного сценария: {summary_rows[0]['p95_total_ms']} мс.",
            "",
            "Таблицы:",
            "- `load_accounts.csv` — каждый бот и итог его сценария.",
            "- `load_steps.csv` — каждый шаг каждого бота.",
            "- `performance_summary.csv` — скорость работы.",
            "- `memory_samples.csv` — сырые замеры `docker stats`.",
            "- `memory_summary.csv` — средняя и максимальная память по контейнерам.",
        ],
    )
    return {"users": users, "summary": summary_rows[0], "bots": bot_rows, "memory": memory_summary, "dir": str(load_dir)}


def load_matrix_rows(load_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in load_results:
        row = dict(result["summary"])
        memory_values = [float(item.get("max_memory_mib") or 0) for item in result.get("memory", [])]
        row["max_container_memory_mib"] = round(max(memory_values), 2) if memory_values else 0
        row["report_dir"] = result["dir"]
        rows.append(row)
    return rows


def write_load_index(out_dir: Path, load_results: list[dict[str, Any]]) -> None:
    matrix = load_matrix_rows(load_results)
    write_csv(out_dir / "load" / "load_matrix.csv", matrix)
    write_markdown(
        out_dir / "load" / "README.md",
        "Нагрузка и память",
        [
            "Этот раздел показывает скорость работы при выбранной нагрузке. Если задано несколько уровней через `--load-steps`, каждый уровень лежит в отдельной подпапке.",
            "",
            "Главные таблицы:",
            "- `load_matrix.csv` — общая таблица скорости и памяти по уровням нагрузки.",
            "- `load_accounts.csv` или `<N>_users/load_accounts.csv` — каждый зарегистрированный бот отдельной строкой.",
            "- `load_steps.csv` или `<N>_users/load_steps.csv` — каждый шаг каждого бота.",
            "- `memory_samples.csv` и `memory_summary.csv` — потребление памяти контейнерами.",
            "",
            f"- Уровней нагрузки: {len(matrix)}",
            f"- Максимальная проверенная нагрузка: {max((row['users'] for row in matrix), default=0)} пользователей",
        ],
    )


def write_root_summary(out_dir: Path, args: argparse.Namespace, results: dict[str, Any]) -> None:
    load_results = results.get("load", [])
    if isinstance(load_results, dict):
        load_results = [load_results]
    summary_rows = [
        {
            "section": "verification",
            "checks": len(results["verification"]["rows"]),
            "ok": sum(1 for row in results["verification"]["rows"] if row["status"] == "OK"),
            "fail": sum(1 for row in results["verification"]["rows"] if row["status"] != "OK"),
        },
        {
            "section": "validation",
            "checks": len(results["validation"]["rows"]),
            "ok": sum(1 for row in results["validation"]["rows"] if row["status"] == "OK"),
            "fail": sum(1 for row in results["validation"]["rows"] if row["status"] != "OK"),
        },
        {
            "section": "usability",
            "checks": len(results["usability"]["rows"]),
            "ok": sum(1 for row in results["usability"]["rows"] if row["status"] == "OK"),
            "fail": sum(1 for row in results["usability"]["rows"] if row["status"] != "OK"),
        },
    ]
    for result in load_results:
        summary = result["summary"]
        summary_rows.append(
            {
                "section": f"load_{summary['users']}_users",
                "checks": summary["users"],
                "ok": summary["successful_scenarios"],
                "fail": summary["failed_scenarios"],
            }
        )

    write_csv(out_dir / "summary.csv", summary_rows)
    write_html_report(
        out_dir / "report.html",
        "QA-отчет Lumin",
        [
            {"title": "Сводка", "rows": summary_rows},
            {"title": "Матрица нагрузки", "rows": load_matrix_rows(load_results)},
            {"title": "Валидация аккаунтов", "rows": results["validation"]["rows"]},
        ],
    )
    write_markdown(
        out_dir / "README.md",
        "QA-отчет Lumin",
        [
            f"Дата запуска: {datetime.now().isoformat(timespec='seconds')}",
            f"Backend URL: `{args.base_url}`",
            f"Frontend URL: `{args.frontend_url}`",
            f"Количество ботов: `{args.users}`",
            f"Уровни нагрузки: `{args.load_steps or args.users}`",
            "",
            "Быстрая сводка: `summary.csv` и `report.html`.",
            "",
            "Разделы отчета:",
            "- `verification/` — проверка доступности и структуры системы.",
            "- `validation/` — проверка правил регистрации и входа.",
            "- `usability/` — проверка frontend-маршрутов и качества тестовых данных.",
            "- `load/` — нагрузка, скорость ответов и память контейнеров.",
        ],
    )


def parse_load_steps(value: str | None, fallback: int) -> list[int]:
    if not value:
        return [max(1, min(100, fallback))]
    numbers: list[int] = []
    for part in re.split(r"[,;\s]+", value.strip()):
        if not part:
            continue
        try:
            number = int(part)
        except ValueError as exc:
            raise SystemExit(f"Некорректный уровень нагрузки: {part}") from exc
        if number < 1 or number > 100:
            raise SystemExit("Нагрузка должна быть от 1 до 100 пользователей")
        if number not in numbers:
            numbers.append(number)
    if not numbers:
        return [max(1, min(100, fallback))]
    return numbers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QA suite for Lumin")
    parser.add_argument("--users", type=int, default=10, help="Количество ботов от 1 до 100")
    parser.add_argument("--load-steps", default="", help="Серия нагрузок, например: 1,10,50,100")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Корень backend")
    parser.add_argument("--frontend-url", default="http://localhost:5173", help="Корень frontend")
    parser.add_argument("--out", default="reports", help="Папка для отчетов")
    parser.add_argument("--timeout", type=float, default=10, help="HTTP timeout в секундах")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    users = max(1, min(100, args.users))
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out) / f"qa_run_{run_id}_{users}_users"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {}
    results["verification"] = run_verification(args.base_url, args.frontend_url, out_dir, args.timeout)
    results["validation"] = run_validation(args.base_url, out_dir, run_id, args.timeout)
    results["usability"] = run_usability(args.base_url, args.frontend_url, out_dir, args.timeout)
    load_steps = parse_load_steps(args.load_steps, users)
    load_results = []
    for count in load_steps:
        section_name = "" if len(load_steps) == 1 else f"{count}_users"
        load_results.append(run_load(args.base_url, out_dir, count, run_id, args.timeout, section_name=section_name))
    write_load_index(out_dir, load_results)
    results["load"] = load_results
    write_root_summary(out_dir, args, results)

    print(f"QA report ready: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
