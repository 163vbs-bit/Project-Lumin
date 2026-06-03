# API Documentation

Interactive OpenAPI documentation is available at `/docs` after the backend starts.

## Auth

- `POST /api/auth/register`: creates a student or teacher.
- `POST /api/auth/login`: returns access and refresh tokens.
- `POST /api/auth/refresh`: rotates token pair from a refresh token.
- `GET /api/auth/me`: returns current authenticated user.

## Tests

- `GET /api/tests`: list published tests with filters.
- `GET /api/tests/categories`: list categories.
- `POST /api/tests`: create a test. Teacher role required.
- `GET /api/tests/{id}`: get test with questions and answers.
- `DELETE /api/tests/{id}`: delete own test. Teacher role required.
- `POST /api/tests/{id}/attempts`: submit answers and receive score.

## Users

- `GET /api/users/me`: profile.
- `GET /api/users/me/history`: latest attempts.
- `GET /api/users/leaderboard`: XP leaderboard.

## Analytics

- `GET /api/analytics/dashboard`: personal dashboard metrics.
- `GET /api/analytics/teacher`: teacher-owned test analytics.
