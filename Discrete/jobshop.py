# 导入simpy库，用于事件驱动的仿真
import simpy

# 定义机器类
class Machine:
    # 初始化函数，为每台机器创建一个资源
    def __init__(self, env, name):
        self.env = env  # 仿真环境
        self.name = name  # 机器名称
        self.resource = simpy.Resource(env, capacity=1)  # 机器资源，每台机器同时只能处理一个任务

    # 机器处理作业的函数
    def process(self, job, duration):
        with self.resource.request() as req:  # 请求机器资源
            yield req  # 等待资源可用
            yield self.env.timeout(duration)  # 模拟任务处理时间
            print(f"Job {job} processed on {self.name} at time {self.env.now}")  # 输出任务处理完成的信息

# 作业处理流程函数
def job_process(env, job, machines, routing, durations):
    for machine_name, duration in zip(routing[job], durations[job]):  # 遍历作业的路由和持续时间
        yield env.process(machines[machine_name].process(job, duration))  # 在指定机器上处理任务

# DFJSS仿真主函数
def dfjss_simulation(routing, durations):
    env = simpy.Environment()  # 创建仿真环境
    # 创建机器字典，每个机器名对应一个机器对象
    machines = {name: Machine(env, name) for name in set(machine for route in routing.values() for machine in route)}

    for job in routing:  # 遍历每个作业
        env.process(job_process(env, job, machines, routing, durations))  # 启动作业处理流程

    env.run()  # 运行仿真

# 示例数据
routing = {
    "Job1": ["MachineA", "MachineB"],
    "Job2": ["MachineB", "MachineA"],
    "Job3": ["MachineA", "MachineB"]
}

durations = {
    "Job1": [5, 3],
    "Job2": [2, 4],
    "Job3": [3, 3]
}

# 启动仿真
dfjss_simulation(routing, durations)
