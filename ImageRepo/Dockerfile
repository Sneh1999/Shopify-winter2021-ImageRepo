FROM python:3.6
WORKDIR /code
ENV FLASK_APP home.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY requirements.txt requirements.txt
RUN pip3 install connexion[swagger-ui]
RUN pip3 install -r requirements.txt
COPY . .
RUN ls
EXPOSE 5000
CMD ["python3", "home.py"]