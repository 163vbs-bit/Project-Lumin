# Load Testing Report

Locust scenarios cover:

- login with demo student;
- listing tests;
- loading dashboard analytics;
- opening leaderboard.

Run:

```bash
locust -f load-tests/locustfile.py --host http://localhost:8000
```

## Performance Targets

| Users | Target P95 Response | Target Error Rate | Expected RAM |
| ---: | ---: | ---: | ---: |
| 10 | < 120 ms | < 0.5% | < 350 MB |
| 100 | < 280 ms | < 1.0% | < 650 MB |
| 500 | < 800 ms | < 2.0% | < 1.4 GB |

## Report Template

| Users | Avg Response | P95 Response | Requests/sec | Errors | Backend RAM |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | TBD | TBD | TBD | TBD | TBD |
| 100 | TBD | TBD | TBD | TBD | TBD |
| 500 | TBD | TBD | TBD | TBD | TBD |

Record RAM with `docker stats` while Locust is running.
