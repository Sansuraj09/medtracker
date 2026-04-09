FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for MySQL to be ready..."\n\
while ! mysqladmin ping -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do\n\
    echo "MySQL is unavailable - sleeping"\n\
    sleep 2\n\
done\n\
echo "MySQL is up - executing initialization"\n\
python init_db.py\n\
echo "Starting Gunicorn..."\n\
exec python -m gunicorn --bind 0.0.0.0:5000 --workers 4 app:app\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]

