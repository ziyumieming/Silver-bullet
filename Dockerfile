# 选择官方 Python 3.12.3 版本作为基础镜像
FROM python:3.12.3-slim

# 避免 tzdata 等需要交互
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖（如构建库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

RUN apt-get update && apt-get install -y redis-server

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
