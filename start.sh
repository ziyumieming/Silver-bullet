#!/bin/bash
# 启动 Redis
redis-server &

# 启动你的应用（FastAPI、Flask、main.py 等）
python app/dispatch.py
