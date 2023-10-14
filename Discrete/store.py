# 导入所需的库
from collections import namedtuple
import simpy

# 使用namedtuple定义一个简单的机器类型，包含大小和使用时长
Machine = namedtuple('Machine', 'size, duration')

# 创建两台机器：m1和m2
m1 = Machine(1, 2)
m2 = Machine(2, 1)


# 用户函数，模拟用户如何请求和使用机器
def user(name, env, ms, size):
    # 用户请求特定大小的机器
    machine = yield ms.get(lambda machine: machine.size == size)
    print(f'{name} got {machine} at {env.now}')

    # 用户使用机器一段时间
    yield env.timeout(machine.duration)

    # 用户释放机器
    yield ms.put(machine)
    print(f'{name} release {machine} at {env.now}')


# 创建模拟环境
env = simpy.Environment()

# 创建一个机器商店，其中包含两台机器
machine_shop = simpy.FilterStore(env, capacity=2)
machine_shop.items = [m1, m2]

# 创建三个用户进程，每个用户都想使用特定大小的机器
user = [env.process(user(i, env, machine_shop, (i % 2) + 1)) for i in range(3)]

# 运行模拟
env.run()
