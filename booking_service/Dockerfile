FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg2 apt-transport-https lsb-release \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Đây là nơi motor và beanie sẽ được cài đặt từ requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy mã nguồn
COPY . /app

# Expose port
EXPOSE 8003

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8003/api/v1/health || exit 1

# Start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]