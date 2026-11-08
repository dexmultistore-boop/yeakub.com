FROM python:3.10-slim

# সিস্টেম লেভেলের জিনিসপত্র ইনস্টল (ffmpeg, libmagic ইত্যাদি)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    libffi-dev \
    libssl-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# পাইথন লাইব্রেরিগুলো ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# বাকি ফাইলগুলো কপি
COPY . .

# পোর্ট এক্সপোজ
EXPOSE 5000

# সার্ভার রান
CMD ["python", "app.py"]