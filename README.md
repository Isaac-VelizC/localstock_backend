# nombre-proyecto-backend

API Backend en Django + DRF

## Requisitos

- Python 3.10+
- pip
- virtualenv (opcional)

## Instalación

```bash
git clone ...
cd nombre-proyecto-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
