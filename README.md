# Launchpad Project

Refactored project structure with packages and modules.

## Project Structure

- `app/`: Main FastAPI application modules
- `app/routes/`: API route definitions
- `app/utils/`: Utility functions (OTP, email, etc.)
- `frontend/`: Static frontend assets
- `alembic/`: Database migration scripts
- `scripts/`: Utility scripts

## Usage

```bash
uvicorn app.main:app --reload
```