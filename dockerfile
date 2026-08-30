FROM python:3.11-slim
WORKDIR /app
RUN pip install psycopg2-binary ldap3
COPY sync_script.py /app/sync_script.py
CMD ["python", "-u","sync_script.py"]