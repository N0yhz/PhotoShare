FROM python:3.12

WORKDIR /app

RUN pip install poetry 

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root

COPY . .

RUN poetry run pip install uvicorn

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "-reload"]