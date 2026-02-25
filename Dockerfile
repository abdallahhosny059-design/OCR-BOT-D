FROM python:3.9-slim-bullseye

WORKDIR /app

# تثبيت الحزم الأساسية فقط (بدون مكونات X11 غير ضرورية)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# تنظيف الكاش لتقليل الحجم
RUN pip cache purge && \
    find /usr/local/lib/python3.9/site-packages -name "*.pyc" -delete

COPY . .

CMD ["python", "main.py"]
