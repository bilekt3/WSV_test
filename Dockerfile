FROM comap.azurecr.io/wsv/python-selenium:b001

WORKDIR /app
COPY . /app

RUN pip install --upgrade -r requirements.txt

ENTRYPOINT ["python"]
CMD ["/app/app.py"]