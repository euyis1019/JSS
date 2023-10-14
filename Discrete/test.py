import simpy

class ListEmptyError(Exception):
    pass
class A:
    def __init__(self, i,env):
        self.items_list = i
        self.env = env

    def add_list(self):
        for i in range(10, 100):
            print(self.env.now)
            yield self.env.timeout(1)
            print(f"At time {self.env.now}, add {i}")
            self.items_list.append(i)

    def process_items(self):
        while True:
            while self.items_list:  # 只要列表不为空
                item = self.items_list.pop(0)  # 取出第一个元素
                # 对元素执行操作
                print(f"At time {env.now}, processing item: {item}")





env = simpy.Environment()

items = [1,2,3]
A = A(items, env)
# 将处理函数添加为进程
env.process(A.process_items())
env.process(A.add_list())

# 运行模拟
env.run(until=10)
