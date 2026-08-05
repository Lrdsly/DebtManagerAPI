# DebtManagerAPI

A complete debt management system built with Django and Django REST Framework, supporting multi-user access, room-based debt tracking, notifications, and detailed logging.

## 🛠 Technologies
1. Python
2. Django
3. DRF (Django REST Framework)
4. SQLite
5. Git / GitHub

## 🚀 Features
- Create, update and manage debts
- User system with multiple access levels (Basic / Premium)
- Managed user permissions (authorization) in custom manager and permission classes
- Create multiple rooms to separate different debt categories
- Room states (Secure / Normal / Semi-secure) for controlled debt confirmation
- Friendship system to prevent spam in public rooms
- Full logging from debt creation to payment
- Notification system for each user
- Custom built in commands to initialize data base | create random data for tests

## Getting start
1. Clone the repository: `git clone https://github.com/Lrdsly/debt-management-api.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py makemigrations && python manage.py migrate`
4. Initialize DB: `python manage.py initial_objects`
5. Run servers: `python manage.py runserver`

## Endpoints & Documentation
Once the project is running, you can access the interactive API documentation via Swagger UI:
- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **OpenAPI Schema:** `http://127.0.0.1:8000/api/schema/`
