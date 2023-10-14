# 导入simpy库，用于仿真
import simpy
# 导入logger，用于日志记录
from logger import logger
# 导入random库，用于生成随机数
import random
# 导入plotly库，用于绘图
import plotly.graph_objects as go
import plotly.offline as pyoff

# 设置随机数种子为1，确保每次运行结果一致
random.seed(1)

# 定义一个简单的服务器类
class SimpleServer:

    # 初始化方法
    def __init__(self, env: simpy.Environment, cpu=100, memory=1000, num_request=10000, num_process=10):
        # 设置环境
        self.env = env
        # 设置CPU容器，用于模拟CPU资源
        self.cpu = simpy.Container(env=env, capacity=cpu, init=cpu)
        # 设置内存容器，用于模拟内存资源
        self.memory = simpy.Container(env=env, capacity=memory, init=memory)
        # 设置请求存储，用于存放待处理的请求
        self.request = simpy.Store(env=env, capacity=simpy.core.Infinity)
        # 启动生产者进程，生成请求
        self.env.process(self.producer(num=num_request))
        # 启动消费者进程，处理请求
        self.c = [self.env.process(self.customer('c{}'.format(_))) for _ in range(num_process)]

    # 生产者方法，用于生成请求
    def producer(self, num=100):
        for i in range(num):
            _item = {'id': i, 'cpu': random.randint(1, 50), 'memory': random.randint(1, 100)}
            yield self.request.put(_item)

    # 消费者方法，用于处理请求
    def customer(self, name):
        """使用customer进程模拟一个进程处理请求的过程：
        获取一个待处理请求 -> 申请cpu和内存资源 -> 处理请求 -> 释放cpu和内存资源。"""
        while True:
            _item = yield self.request.get()
            logger.info('time: {}, {} get request: {}'.format(round(self.env.now, 2), name, _item))
            _cpu = _item['cpu']
            _mem = _item['memory']
            cpu_rq = self.cpu.get(_cpu)
            mem_rq = self.memory.get(_mem)
            logger.info('{} wait for resource: cpu {}, mem {}'.format(name, _cpu, _mem))
            _ck = yield cpu_rq & mem_rq
            logger.info('time: {}, {} deal with request: {}'.format(round(self.env.now, 2), name, _item['id']))
            yield self.env.timeout(0.1)

            yield self.cpu.put(_cpu)
            yield self.memory.put(_mem)
            logger.info('time: {}, {} put back resouce'.format(round(self.env.now, 2), name))

# 设置日志级别为WARNING
logger.setLevel('WARNING')

# 测试函数
def test():
    x = []
    y = []
    # 遍历进程数量，模拟不同的进程数量对处理时间的影响
    for num_process in range(1, 21):
        _env = simpy.Environment()
        sm = SimpleServer(_env, num_request=10000, num_process=num_process)
        _env.run()
        x.append(num_process)
        y.append(_env.now)
    # 绘制图形
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+lines'
    ))
    fig.update_layout(xaxis=dict(title='进程数量'), yaxis=dict(title='时间'), font_size=22)
    pyoff.plot(fig)

# 主函数入口
if __name__ == '__main__':
    test()
