import json
from utils import get_page , is_valid_ip_port, extract_fps_list
from pyquery import PyQuery as pq

from store import RedisClient

POOL_UPPER_THRESHOLD = 10000


class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count1 = 0
        count2 = 0
        attrs['__CrawlInnerFunc__'] = []
        attrs['__CrawlOuterFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_inner_' in k:
                attrs['__CrawlInnerFunc__'].append(k)
                count1 += 1
            elif 'crawl_outer_' in k:
                attrs['__CrawlOuterFunc__'].append(k)
                count2 += 1
        attrs['__CrawlInnerFuncCount__'] = count1
        attrs['__CrawlOuterFuncCount__'] = count2
        return type.__new__(cls, name, bases, attrs)

class Crawler(object, metaclass=ProxyMetaclass):
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print('成功获取到代理', proxy)
            proxies.append(proxy)
        return proxies

    def crawl_inner_89ip(self,num=60):
        start_url = f'http://api.89ip.cn/tqdl.html?api=1&num={num}&port=&address=&isp='
        print('Crawling', start_url)
        html = get_page(start_url)
        if html:
            doc = pq(html).text()
            ip_port_list = [line.strip() for line in doc.split() if line.strip()and is_valid_ip_port(line.strip())]
            print('获取到代理', ip_port_list)
            return ip_port_list

    def crawl_inner_scdn(self, num=60):
        start_url = f'https://proxy.scdn.io/api/get_proxy.php'
        params = {
            'protocol': 'all',
            'count': num
        }
        print('Crawling', start_url)
        html = get_page(start_url, params=params)
        if html:
            data = json.loads(html)
            ip_port_list = [proxy for proxy in data.get('data', {}).get('proxies', [])]
            print('获取到代理', ip_port_list)
            return ip_port_list

    def crawl_inner_ip3366(self,num=60):
        page = 1
        num_now = 0
        proxies = []
        while num_now < num:
            start_url = f'http://www.ip3366.net/free/?stype=1&page={page}'
            print('Crawling', start_url)
            html = get_page(start_url)
            if html:
                doc = pq(html)
                # 使用 CSS 选择器定位元素
                table = doc('#container #list table')
                # 获取所有行，跳过表头行
                trs = table('tr:gt(0)')
                for tr in trs.items():
                    # 获取前两个 td 的文本内容
                    ip = tr('td:eq(0)').text().strip()
                    port = tr('td:eq(1)').text().strip()
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
                    # 如果已经获取了足够数量的代理，则停止
                    if len(proxies) >= num:
                        break
                num_now = len(proxies)
            page += 1
            if page > 10:  # 防止无限循环
                break
        print('获取到代理', proxies)
        return proxies

    def crawl_inner_zdaye(self,num=60):
        page = 1
        num_now = 0
        proxies = []
        while num_now < num:
            start_url = f'https://www.zdaye.com/free/{page}/'
            print('Crawling', start_url)
            html = get_page(start_url)
            if html:
                doc = pq(html)
                # 使用 CSS 选择器定位元素
                table = doc('.top .abox table')
                # 获取所有行，跳过表头行
                trs = table('tr:gt(0)')
                for tr in trs.items():
                    # 获取前两个 td 的文本内容
                    ip = tr('td:eq(0)').text().strip()
                    port = tr('td:eq(1)').text().strip()
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
                    # 如果已经获取了足够数量的代理，则停止
                    if len(proxies) >= num:
                        break
                num_now = len(proxies)
            page += 1
            if page > 10:  # 防止无限循环
                break
        print('获取到代理', proxies)
        return proxies

    def crawl_inner_kuaidaili(self,num=60):
        page = 1
        num_now = 0
        proxies = []
        while num_now < num:
            start_url = f'https://www.kuaidaili.com/free/dps/{page}/'
            print('Crawling', start_url)
            html = get_page(start_url)
            if html:
                doc = pq(html)
                fps_list = extract_fps_list(html)
                if fps_list:
                    for fps in fps_list:
                        # print ('fps:', fps)
                        status = fps.get('is_valid')
                        if status == False:
                            print('获取到代理', proxies)
                            return proxies
                        ip = fps.get('ip')
                        port = fps.get('port')
                        proxy = f"{ip}:{port}"
                        proxies.append(proxy)
                        # 如果已经获取了足够数量的代理，则停止
                        if len(proxies) >= num:
                            break
                num_now = len(proxies)
            page += 1
            if page > 10:  # 防止无限循环
                break
        print('获取到代理', proxies)
        return proxies

    def crawl_outer_geonode(self, num=60):
        start_url = f'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'
        print('Crawling', start_url)
        html = get_page(start_url)
        if html:
            data = json.loads(html)
            ip_port_list = [str(proxy.get('ip')) + ':' + str(proxy.get('port')) for proxy in data.get('data', {})]
            print('获取到代理', ip_port_list)
            return ip_port_list


class Getter():
    def __init__(self, redis_key='proxies_inner'):
        self.kind=redis_key 
        self.redis = RedisClient(redis_key=redis_key)
        self.crawler = Crawler()

    def is_over_threshold(self):
        """
        判断是否达到了代理池限制
        """
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def _crawl_inner(self):
        for callback_label in range(self.crawler.__CrawlInnerFuncCount__):
            callback = self.crawler.__CrawlInnerFunc__[callback_label]
            proxies = self.crawler.get_proxies(callback)
            for proxy in proxies:
                self.redis.add(proxy)

    def _crawl_outer(self):
        for callback_label in range(self.crawler.__CrawlOuterFuncCount__):
            callback = self.crawler.__CrawlOuterFunc__[callback_label]
            proxies = self.crawler.get_proxies(callback)
            for proxy in proxies:
                self.redis.add(proxy)

    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            if self.kind == 'proxies_inner':
                self._crawl_inner()
            elif self.kind == 'proxies_outer':
                self._crawl_outer()


# crawler = Crawler()
# proxies = crawler.crawl_outer_freeproxy(num=5)
# print('代理数目:', len(proxies))
