# Single-stage image cho đơn giản và đáng tin cậy
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Cài các công cụ hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg2 apt-transport-https lsb-release build-essential \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Thêm key Microsoft và repository theo cách an toàn (gpg --dearmor)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update \
 && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy mã nguồn
COPY . /app

# Expose port
EXPOSE 8003

# Healthcheck (yêu cầu curl trong image)
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8003/api/v1/health || exit 1

# Start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]