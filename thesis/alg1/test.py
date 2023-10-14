import random

from thesis.alg1.common import get_random_config
from thesis.job_shop_simulator import *


def arrange_source_operations(source_operations: list[SimOperation], status: Status, operator: Operator):
    machine_to_operations = dict()
    for source_operation in source_operations:
        machines = status.get_operation_machines(source_operation.id, lambda m: not m.get_attribute("running"))
        if len(machines) != 0:
            machine_to_operations.setdefault(random.choice(machines).id, []).append(source_operation)
    for machine_id, operations in machine_to_operations.items():
        operation = random.choice(operations)
        operator.arrange_machine(machine_id, status.operation_machine_raw(operation.id,
                                                                          machine_id).get_attribute("process_time"))
        machine = status.machine(machine_id)
        machine.set_attribute("running", True)
        machine.set_attribute("operation_id", operation.id)
        operation.set_attribute("processing", True)


def clean_operation(operation_id: UUID, status: Status, operator: Operator):
    job = status.get_operation_job(operation_id)
    operator.delete_operation(operation_id)
    operations = status.get_job_operations(job.id)
    if len(operations) == 0:
        operator.delete_job(job.id)


def reset_machine(machine_id: UUID, status: Status):
    machine = status.machine(machine_id)
    operation_id = machine.get_attribute("operation_id")
    machine.set_attribute("operation_id", None)
    machine.set_attribute("running", False)
    return operation_id


class Test(Algorithm):
    def __init__(self):
        pass

    def on_operation_finished(self, machine_id: UUID, status: Status, operator: Operator) -> None:
        operation_id = reset_machine(machine_id, status)
        clean_operation(operation_id, status, operator)
        source_operations = status.get_all_source_operations(lambda op: not op.get_attribute("processing"))
        arrange_source_operations(source_operations, status, operator)

    def on_job_arrived(self, job_id: UUID, status: Status, operator: Operator) -> None:
        source_operations = status.get_job_source_operations(job_id)
        arrange_source_operations(source_operations, status, operator)

    def on_decide_job_arrive_time(self, job: Job) -> SimTime:
        return job.get_attribute("arrive_time")

    def on_init_machine(self, machine: SimMachine):
        machine.set_attribute("operation_id", None)
        machine.set_attribute("running", False)


jobs = [Job("1", {"arrive_time": 10}), Job("2", {"arrive_time": 6})]
operations = [Operation("1-1"), Operation("1-2"), Operation("2-1")]
machines = [Machine(1), Machine(2)]
job_operations = [JobOperation("1", "1-1"), JobOperation("1", "1-2"), JobOperation("2", "2-1")]
operation_relations = [OperationRelation("1-1", "1-2", {"transmit_time": 6})]
operation_machines = [OperationMachine("1-1", 1, {"process_time": 3}),
                      OperationMachine("1-2", 2, {"process_time": 5}),
                      OperationMachine("2-1", 1, {"process_time": 4})]

config = Config(jobs, operations, machines, job_operations, operation_relations, operation_machines, None)

instance = Instance(get_random_config(200, 5, 10, 10, 1, 10, 0.95), Test())

instance.run()

print(instance.now)
