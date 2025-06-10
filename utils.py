import requests
import re
import json

def get_page(url, params=None, headers=None, timeout=10,cookies=None):
    """
    获取指定 URL 的 HTML 内容
    :param url: 请求的 URL
    :param headers: 请求头（可选）
    :param timeout: 超时时间（默认 10 秒）
    :return: HTML 内容（字符串），如果请求失败则返回 None
    """
    try:
        # 设置默认的请求头
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'cookie': cookies if cookies else ''
            }
        # 发送 GET 请求
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        # 检查 HTTP 状态码
        if response.status_code == 200:
            return response.text  # 返回 HTML 内容
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"请求发生错误: {e}")
        return None



def is_valid_ip_port(line):
    """
    判断一行字符串是否是合法的 IP 地址和端口号形式
    :param line: 输入字符串
    :return: 如果合法返回 True，否则返回 False
    """
    # 正则表达式匹配 IP 地址和端口号
    pattern = r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
    if re.match(pattern, line):
        # 检查 IP 地址的每一段是否在 0-255 范围内
        ip, port = line.split(':')
        ip_parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in ip_parts):
            # 检查端口号是否在 1-65535 范围内
            if 1 <= int(port) <= 65535:
                return True
    return False


def extract_fps_list(html):
    """
    从 HTML 响应中提取 const fpsList 的内容
    :param html: HTML 响应内容
    :return: 解析后的 fpsList 数据
    """
    try:
        # 使用正则表达式定位包含 fpsList 的 <script> 标签
        script_pattern = re.compile(r'<script type="text/javascript">.*?const fpsList\s*=\s*(\[.*?\]);', re.S)
        match = script_pattern.search(html)
        if match:
            # 提取 const fpsList 的 JSON 内容
            fps_list_json = match.group(1)
            # 将 JSON 字符串解析为 Python 数据结构
            fps_list = json.loads(fps_list_json)
            return fps_list
        else:
            print("未找到 fpsList 定义")
            return None
    except Exception as e:
        print(f"解析 fpsList 时出错: {e}")
        return None