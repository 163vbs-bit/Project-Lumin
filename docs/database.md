# Database Schema

```mermaid
erDiagram
  roles ||--o{ users : has
  users ||--o{ tests : authors
  users ||--o{ attempts : makes
  users ||--o{ statistics : owns
  users ||--o{ user_progress : tracks
  categories ||--o{ tests : groups
  categories ||--o{ statistics : summarizes
  categories ||--o{ user_progress : measures
  tests ||--o{ questions : contains
  questions ||--o{ answers : offers
  tests ||--o{ attempts : receives
  users }o--o{ achievements : unlocks

  users {
    int id
    string email
    string username
    string hashed_password
    int role_id
    int xp
    int level
    int streak
  }

  tests {
    int id
    string title
    string difficulty
    string mode
    int category_id
    int author_id
  }

  attempts {
    int id
    int user_id
    int test_id
    int score
    float percent
    json answers_payload
  }
```

Alembic migration `0001_initial_schema.py` creates all required tables:

- `users`
- `roles`
- `tests`
- `categories`
- `questions`
- `answers`
- `attempts`
- `statistics`
- `achievements`
- `user_progress`
- `user_achievements`
