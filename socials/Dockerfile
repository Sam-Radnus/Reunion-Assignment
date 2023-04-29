
FROM python:3.10.6-slim-buster

RUN mkdir /REUNION

WORKDIR /REUNION

COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install PostgreSQL client
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y postgresql-client libpq-dev

# Copy the rest of the application code into the container at /REUNION
COPY . /REUNION/

# Expose port 8000 for the Django app to listen on
EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
