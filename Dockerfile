FROM python:3.14.6
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python","-u", "app.py"]