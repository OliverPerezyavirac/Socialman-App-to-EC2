FROM python:3.12

WORKDIR /app
COPY requeriments.txt requeriments.txt
RUN pip install --no-cache-dir -r requeriments.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
 