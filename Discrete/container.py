import simpy

def consumer(bucket):
    yield env.timeout(1)
    while True:
        yield bucket.get(10)  # 每次取10升水
        print(f"Time {env.now}: Consumer took 10 liters. Remaining water: {bucket.level} liters.")
        yield env.timeout(1)  # 每1个时间单位取一次

def producer(bucket):
    yield env.timeout(3)  # 等待3个时间单位再开始加水
    while True:
        yield bucket.put(5)  # 每次加5升水
        print(f"Time {env.now}: Producer added 5 liters. Total water: {bucket.level} liters.")
        yield env.timeout(0.5)  # 每0.5个时间单位加一次

env = simpy.Environment()
bucket = simpy.Container(env, capacity=100, init=50)
print(f"Initial water in bucket: {bucket.level} liters.")

env.process(consumer(bucket))
env.process(producer(bucket))
env.run(until=10)  # 运行10个时间单位
