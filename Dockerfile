FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code

RUN apt-get update
RUN apt-get install -y nano
RUN pip install --upgrade pip
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# export port
EXPOSE 5000



# docker run後容器不要關閉



COPY . /code/

# CMD [ "tail", "-f", "/dev/null" ]

CMD ["python", "manage.py", "runserver","0.0.0.0:5000"]