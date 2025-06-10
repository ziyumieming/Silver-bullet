from flask import Flask, g
from store import RedisClient
from flask import request

__all__ = ['app']
app = Flask(__name__)

# 全局只创建一个 RedisClient 实例
redis_client = RedisClient()


def get_conn(redis_key=None):
    # 每次只切换 key，不重新创建 RedisClient
    redis_client.redis_key = redis_key or 'proxies'
    return redis_client

@app.route('/')
def index():
    return '<h2>Welcome to Proxy Pool System</h2>'

@app.route('/site')
def get_proxy():
    """
    获取随机可用代理
    :return: 随机代理
    """
    redis_key = request.args.get('key', 'proxies_inner')
    conn = get_conn(redis_key)
    return conn.random()

@app.route('/count')
def get_counts():
    """
    获取代理池总量
    :return: 代理池总量
    """
    redis_key = request.args.get('key', 'proxies_inner')
    conn = get_conn(redis_key)
    return str(conn.count())

if __name__ == '__main__':
    app.run()