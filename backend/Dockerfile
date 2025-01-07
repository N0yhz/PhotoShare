FROM python:3.12

RUN apt-get update && \
    apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "-reload"]