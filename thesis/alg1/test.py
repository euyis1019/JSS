import random

from thesis.job_shop_simulator import *


def arrange_source_operations(source_operations: list[SimOperation], status: Status, operator: Operator):
    # 初始化一个字典，用于将机器映射到其相应的操作。
    machine_to_operations = dict()
    # 遍历source_operations列表中的每个操作。
    for source_operation in source_operations:
        # 获取当前没有运行任何操作的机器列表。
        machines = status.get_filter_machine(source_operation.id, lambda m: not m.get_attribute("running"))
        # 如果有可用的机器，随机选择一个并将操作映射到它。
        if len(machines) != 0:
            machine_to_operations.setdefault(random.choice(machines).id, []).append(source_operation.id)

    # 遍历每台机器及其关联的操作。
    for machine_id, operation_ids in machine_to_operations.items():
        # 为机器随机选择一个操作。
        operation_id = random.choice(operation_ids)

        # 使用operator的arrange_machine方法为机器调度所选操作。
        # 该方法需要机器的ID、操作的ID以及完成操作所需的时间。
        operator.arrange_machine(machine_id, status.operation_machine_raw(operation_id,
                                                                          machine_id).get_attribute("operation_time"))

        # 更新机器的状态，表示它现在正在运行一个操作，并设置其当前的操作ID。
        machine = status.machine(machine_id)
        machine.set_attribute("running", True)
        machine.set_attribute("operation_id", operation_id)


def clean_operation(machine_id: UUID, status: Status, operator: Operator):
    #获取机器
    machine = status.machine(machine_id)
    operation_id = machine.get_attribute("operation_id")
    machine.set_attribute("operation_id", None)
    machine.set_attribute("running", False)

    job = status.get_operation_job(operation_id)
    operator.delete_operation(operation_id)
    operations = status.get_job_operations(job.id)
    if len(operations) == 0:
        operator.delete_job(job.id)


class Test(Algorithm):
    def __init__(self):
        pass

    def on_operation_finished(self, machine_id: UUID, status: Status, operator: Operator) -> None:
        clean_operation(machine_id, status, operator)
        source_operations = status.get_all_source_operations()
        arrange_source_operations(source_operations, status, operator)


    """报错点,这里应该是不完善
            这里应该要判断一下，如果当前操作的job是source_job，那么就直接返回，
            因为source_job的source_operation已经全部执行完毕，不需要再执行了。"""
    def on_job_arrived(self, job_id: UUID, status: Status, operator: Operator) -> None:
        #这里我想打印job_id的编号
        print("on_job_arrived-----begin")
        print( status.job_raw(job_id).id)
        source_operations = status.get_job_source_operations(job_id)
        print(status.operation_raw(source_operations[0]).id)
        arrange_source_operations(source_operations, status, operator)
        """报错点"""

    def on_decide_job_arrive_time(self, job: Job) -> SimTime:
        return job.get_attribute("arrive_time")

    def on_init_machine(self, machine: SimMachine):
        machine.set_attribute("operation_id", None)
        machine.set_attribute("running", False)


jobs = [Job(2, {"arrive_time": 5})]
jobs.append(Job(1, {"arrive_time": 3}))
operations = [Operation(11), Operation(12)]
operations.append(Operation(21))
machines = [Machine(3)]
job_operations = [JobOperation(1, 11), JobOperation(1, 12)]
job_operations.append(JobOperation(2, 21))
operation_relations = [OperationRelation(11, 12)]
operation_machines = [OperationMachine(11, 3, {"operation_time": 3}),
                      OperationMachine(12, 3, {"operation_time": 5}),
                                            OperationMachine(21, 3, {"operation_time": 10})]

config = Config(jobs, operations, machines, job_operations, operation_relations, operation_machines, None)

instance = Instance(config, Test())

instance.run()

print(instance._env.now)
