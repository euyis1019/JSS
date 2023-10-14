"""所有资源都有相同的基础定义：
资源本身就是一种容器，通常容量有限。
进程可以从资源里执行放取操作，如果资源满了或者空了，必需排队等待"""

import simpy
env = simpy.Environment()
res = simpy.PreemptiveResource(env, capacity=1)

def resource_user(name, env, resource, wait, prio):
    yield env.timeout(wait)
    with resource.request(priority=prio) as req:
        print(f'{name} requesting at {env.now} with priority={prio}')
        yield req
        print(f'{name} got resource at {env.now}')
        try:
            yield env.timeout(3)
            print(f'{name} released resource at {env.now}')
        except simpy.Interrupt as interrupt:
            by = interrupt.cause.by
            usage = env.now - interrupt.cause.usage_since
            print(f'{name} got preempted by {by} at {env.now}'
                  f'after {usage}')

p1 = env.process(resource_user(1, env, res, wait=0, prio=0))
p2 = env.process(resource_user(2, env, res, wait=1, prio=0))
p3 = env.process(resource_user(3, env, res, wait=2, prio=-1))
env.run()
