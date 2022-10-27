FROM python:3.10

WORKDIR /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip3 install pipenv
RUN pipenv install --system --deploy

COPY . .

CMD ["python", "main.py"]