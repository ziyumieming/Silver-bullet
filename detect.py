import asyncio
import aiohttp
import time
from store import RedisClient
from aiohttp import ClientError, ClientConnectorError, ServerTimeoutError

VALID_STATUS_CODES = [200, 201]
TEST_URL = 'http://www.baike.baidu.com'
BATCH_TEST_SIZE = 10

class Tester(object):
    def __init__(self, redis_key='proxies', test_url='http://www.baike.baidu.com'):
        self.redis = RedisClient(redis_key=redis_key)
        self.test_url = test_url


    async def test_single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy: 单个代理
        :return: None
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(self.test_url, proxy=real_proxy, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法', proxy)
            except (ClientError, ClientConnectorError, ServerTimeoutError, AttributeError, asyncio.TimeoutError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

    def run(self):
        """
        测试主函数（修复版本）- 使用单一事件循环
        :return: None
        """
        print('测试器开始运行')
        try:
            # 方案1：将整个过程改为异步，只使用一个 asyncio.run()
            asyncio.run(self._run_all_async())
        except Exception as e:
            print('测试器发生错误', e.args)

    async def _run_all_async(self):
        """
        完整的异步运行流程
        """
        proxies = self.redis.all()
        # 批量测试
        for i in range(0, len(proxies), BATCH_TEST_SIZE):
            test_proxies = proxies[i:i + BATCH_TEST_SIZE]
            await self._run_batch(test_proxies)
            await asyncio.sleep(15)  # 使用异步睡眠

    async def _run_batch(self, test_proxies):
        """
        运行一批代理测试的辅助方法
        """
        tasks = [asyncio.create_task(self.test_single_proxy(proxy)) for proxy in test_proxies]
        await asyncio.gather(*tasks, return_exceptions=True)

    # 另一种同步方案（如果必须在同步环境中运行）
    def run_sync_safe(self):
        """
        安全的同步运行方法
        """
        print('测试器开始运行')
        try:
            proxies = self.redis.all()
            
            # 获取或创建事件循环
            try:
                loop = asyncio.get_running_loop()
                print("检测到运行中的事件循环，使用新线程")
                # 如果已有事件循环在运行，使用线程池
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for i in range(0, len(proxies), BATCH_TEST_SIZE):
                        test_proxies = proxies[i:i + BATCH_TEST_SIZE]
                        future = executor.submit(self._run_batch_sync, test_proxies)
                        future.result()  # 等待完成
                        time.sleep(15)
            except RuntimeError:
                # 没有运行中的事件循环，可以安全使用 asyncio.run()
                for i in range(0, len(proxies), BATCH_TEST_SIZE):
                    test_proxies = proxies[i:i + BATCH_TEST_SIZE]
                    asyncio.run(self._run_batch(test_proxies))
                    time.sleep(15)
        except Exception as e:
            print('测试器发生错误', e.args)

    def _run_batch_sync(self, test_proxies):
        """
        在新事件循环中运行批处理的同步包装器
        """
        asyncio.run(self._run_batch(test_proxies))

    # 推荐的完全异步方法
    async def run_async(self):
        """
        异步测试主函数（推荐使用）
        :return: None
        """
        print('测试器开始运行')
        try:
            proxies = self.redis.all()
            # 批量测试
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i:i + BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(15)
        except Exception as e:
            print('测试器发生错误', e.args)

# 使用示例
if __name__ == '__main__':
    tester = Tester()
    
    # 推荐方案：使用修复后的 run() 方法
    tester.run()
    
    # 或者直接使用异步方法
    # asyncio.run(tester.run_async())
    
    # 如果在其他异步环境中调用，使用安全的同步方法
    # tester.run_sync_safe()