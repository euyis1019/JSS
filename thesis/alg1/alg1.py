import statistics

from thesis.job_shop_simulator import *


def MWT(machine_id: UUID, status):
    machine = status.machine(machine_id)
    if machine.get_attribute("running"):
        ft = machine.get_attribute("free_time")
        return ft - status.now()
    return 0


def PT(operation_id: UUID, machine_id: UUID, status):
    operation_machine: OperationMachine = status.operation_machine_raw(operation_id, machine_id)
    return operation_machine.get_attribute("process_time")


def OWT(operation_id: UUID, status):
    operation: SimOperation = status.operation(operation_id)
    return status.now() - operation.get_attribute("start_waiting_time")


def WRK_NOR(operation_id: UUID, status):
    job_id: UUID = status.get_operation_job(operation_id).id
    operations: list[SimOperation] = status.get_job_operations(job_id)
    return sum(operation.get_attribute("median_process_time") for operation in operations), len(operations)


def TIS(status):
    return status.now()


def terminals(operation_id: UUID, machine_id: UUID, status):
    return (MWT(machine_id, status),
            PT(operation_id, machine_id, status),
            OWT(operation_id, status),
            *WRK_NOR(operation_id, status),
            TIS(status))


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
    machine.set_attribute("free_time", None)
    return operation_id


class Alg1(Algorithm):
    def __init__(self, routing, sequencing):
        self.routing = routing
        self.sequencing = sequencing

    def on_operation_finished(self, machine_id: UUID, status, operator) -> None:
        operation_id = reset_machine(machine_id, status)
        clean_operation(operation_id, status, operator)
        source_operations = status.get_all_source_operations(lambda op: not op.get_attribute("processing"))
        for source_operation in source_operations:
            if not source_operation.get_attribute("start_waiting_time"):
                source_operation.set_attribute("start_waiting_time", status.now())
        self.arrange_source_operations(source_operations, status, operator)

    def on_job_arrived(self, job_id: UUID, status, operator) -> None:
        operations = status.get_job_operations(job_id)
        for operation in operations:
            operation_machines = status.operation_machines_raw(operation.id)
            operation.set_attribute("median_process_time",
                                    statistics.median([operation_machine.get_attribute("process_time")
                                                       for operation_machine in operation_machines]))
        source_operations: list[SimOperation] = status.get_job_source_operations(job_id)
        for source_operation in source_operations:
            source_operation.set_attribute("start_waiting_time", status.now())
        self.arrange_source_operations(source_operations, status, operator)

    def on_decide_job_arrive_time(self, job: Job) -> SimTime:
        return job.get_attribute("arrive_time")

    def on_init_machine(self, machine: SimMachine) -> None:
        machine.set_attribute("running", False)

    def arrange_source_operations(self, source_operations: list[SimOperation], status: Status, operator: Operator):
        free_machine_to_operations = dict()

        for source_operation in source_operations:
            machines = status.get_operation_machines(source_operation.id)
            free_machine_ids = set(free_machine.id
                                   for free_machine in filter(lambda m: not m.get_attribute("running"), machines))
            if len(free_machine_ids) != 0:
                if len(machines) == 1:
                    choose_machine_id = machines[0].id
                else:
                    scores = [(machine.id, self.routing(*terminals(source_operation.id, machine.id, status)))
                              for machine in machines]
                    choose_machine_id = max(scores, key=lambda m: m[-1])[0]
                if choose_machine_id in free_machine_ids:
                    free_machine_to_operations.setdefault(choose_machine_id, []).append(source_operation)
        for machine_id, operations in free_machine_to_operations.items():
            if len(operations) == 1:
                choose_operation = operations[0]
            else:
                scores = [(operation, self.sequencing(*terminals(operation.id, machine_id, status)))
                          for operation in operations]
                choose_operation = max(scores, key=lambda o: o[-1])[0]
            process_time = status.operation_machine_raw(choose_operation.id, machine_id).get_attribute("process_time")
            operator.arrange_machine(machine_id, process_time)
            machine = status.machine(machine_id)
            machine.set_attribute("running", True)
            machine.set_attribute("operation_id", choose_operation.id)
            machine.set_attribute("free_time", status.now() + process_time)
            choose_operation.set_attribute("processing", True)
