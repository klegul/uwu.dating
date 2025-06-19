FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY . .

RUN poetry install

EXPOSE 5000

CMD [ "poetry", "run", "flask", "--app", "uwu_dating", "run", "--host=0.0.0.0"]
