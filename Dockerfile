FROM tiangolo/uwsgi-nginx-flask:python3.10
LABEL maintainer="Ricardo Legorreta H. AI Legorreta, 2023"

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY ./requirements.txt /var/www/requirements.txt

# Before install the python packages declared requirements.txt we need to upgrade pip3 version store inside the image
RUN pip install --no-cache-dir --upgrade -r /var/www/requirements.txt

# Copy the source code
COPY ./app /app
