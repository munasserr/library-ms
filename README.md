# Library Management System

A modern library management system built with Django REST Framework, featuring user authentication, book management and loan tracking.

## Features
- User authentication and authorization
- Book management
- Loan tracking
- User profile management
- Admin dashboard
- API documentation with Swagger
- Comprehensive test coverage

## Prerequisites
- Docker Desktop installed and running
- Git

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/munasserr/library-ms.git
cd library-ms
```

2. Create a `.env` file in the root directory with the following content:
```env
# db
POSTGRES_DB = postgres
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
POSTGRES_HOST = db
POSTGRES_PORT = 5432

# django
SECRET_KEY = '' Generate a key from https://djecrety.ir/
DEBUG = True
ALLOWED_HOSTS = ['*']
```

3. Build and start the containers:
```bash
docker compose build
docker compose up -d
```

4. Run migrations inside the django-api container:
```bash
docker exec -it django-api python manage.py makemigrations
docker exec -it django-api python manage.py migrate
```

5. Create a superuser:
```bash
docker exec -it django-api python manage.py createsuperuser
```

## Accessing the Application

- Admin Panel: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/swagger/
- API Schema: http://localhost:8000/api/schema/

## Testing

To run the test suite:
```bash
docker exec -it django-api pytest -v
```

## API Documentation

You can access the API documentation in two ways:
1. Through the Swagger UI at http://localhost:8000/swagger/
2. Import the OpenAPI schema from http://localhost:8000/api/schema/ into your preferred API client (like Postman)

## Project Structure
```
src/
├── apps/
│   ├── users/         # User management
│   ├── library/       # library catalog
├── config/            # Project configuration
```

## Contact

For any questions or help, feel free to reach out:
- LinkedIn: [Muhammad Nasser](https://www.linkedin.com/in/munasser/)
