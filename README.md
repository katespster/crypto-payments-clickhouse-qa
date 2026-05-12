# Crypto Payments ClickHouse QA Lab

Portfolio QA Automation project for testing a simplified crypto payments system.

The project demonstrates practical experience with:

- API testing
- Python + Pytest automation
- Allure reporting
- SQL validation
- ClickHouse analytics checks
- Test data management
- CI-ready test execution
- Crypto payments domain basics: deposits, withdrawals, transaction statuses, KYT/Travel Rule related checks

> This is a portfolio / educational project.  
> No real blockchain transactions, wallets, private keys, or real funds are used.

---

## Project Goal

The goal of this project is to demonstrate how a QA Engineer can test a backend payments system in the crypto domain.

The test suite covers typical payment scenarios such as:

- creating crypto deposits;
- creating crypto withdrawals;
- validating payment statuses;
- checking negative API cases;
- validating data saved in ClickHouse;
- attaching request/response payloads to Allure reports;
- preparing the project for CI execution.

This project is especially useful for demonstrating hands-on experience with backend QA, API testing, SQL, Pytest, Allure, and payment domain testing.

---

## Tech Stack

| Area | Tools |
|---|---|
| Language | Python |
| Test framework | Pytest |
| Reporting | Allure |
| API testing | requests / custom API client |
| Database validation | ClickHouse |
| Configuration | environment variables / `.env` |
| CI-ready execution | GitLab CI / GitHub Actions compatible |
| Test design | positive, negative, boundary, equivalence classes |

---
How to install

1) Clone repository via git clone
2) Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1
3) install dependencies
pip install -r requirements.txt
4) start clickhouse container
docker compose up -d
5) if it is need, connect to clickhouse db
docker exec -it clickhouse-qa-lab clickhouse-client
6) run tests with allure report
python -m pytest -v
python -m pytest --alluredir=allure-results
7) open allure report
allure serve allure-results

docker compose up -d

docker exec -it clickhouse-qa-lab clickhouse-client 
Open and work with DB
exit