from typing import Callable

from .sim_component import *


class Status:
    def __init__(self, instance):
        self._instance = instance

    def now(self):
        return self._instance.now

    def job(self, job_id: UUID) -> SimJob:
        return self._instance.jobs[job_id]

    def job_raw(self, job_id: UUID) -> Job:
        return self.job(job_id).raw

    def operation(self, operation_id: UUID) -> SimOperation:
        return self._instance.operations[operation_id]

    def operation_raw(self, operation_id: UUID) -> Operation:
        return self.operation(operation_id).raw

    def machine(self, machine_id: UUID) -> SimMachine:
        return self._instance.machines[machine_id]

    def machine_raw(self, machine_id: UUID) -> Machine:
        return self.machine(machine_id).raw

    def job_operation(self, job_id: UUID, operation_id: UUID) -> SimJobOperation:
        return self._instance.job_operations[job_id][operation_id]["sim"]

    def job_operation_raw(self, job_id: UUID, operation_id: UUID) -> JobOperation:
        return self.job_operation(job_id, operation_id).raw

    def operation_relation(self, from_operation_id: UUID, to_operation_id: UUID) -> SimOperationRelation:
        return self._instance.operation_relations[from_operation_id][to_operation_id]["sim"]

    def operation_relation_raw(self, from_operation_id: UUID, to_operation_id: UUID) -> OperationRelation:
        return self.operation_relation(from_operation_id, to_operation_id).raw

    def operation_machine(self, operation_id: UUID, machine_id: UUID) -> SimOperationMachine:
        return self._instance.operation_machines[operation_id][machine_id]["sim"]

    def operation_machine_raw(self, operation_id: UUID, machine_id: UUID) -> OperationMachine:
        return self.operation_machine(operation_id, machine_id).raw

    def operation_machines(self, operation_id: UUID) -> list[SimOperationMachine]:
        return [attrs["sim"] for attrs in self._instance.operation_machines[operation_id].values()]

    def operation_machines_raw(self, operation_id: UUID) -> list[OperationMachine]:
        return [attrs["raw"]
                for attrs in self._instance.config.operation_machines[self.operation(operation_id).raw.id].values()]

    def get_job_operations(self, job_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id] for operation_id in self._instance.job_operations[job_id]]

    def get_job_operations_raw(self, job_id: UUID) -> list[Operation]:
        return [self._instance.config.operations[raw_operation_id]
                for raw_operation_id in self._instance.config.job_operations[self.job(job_id).raw.id]]

    def get_operation_job(self, operation_id: UUID) -> SimJob:
        return [self._instance.jobs[job_id] for job_id in self._instance.job_operations[operation_id]][0]

    def get_operation_job_raw(self, operation_id: UUID) -> Job:
        return self.get_operation_job(operation_id).raw

    def get_operation_machines(self, operation_id: UUID,
                               machine_filter: Callable[[SimMachine], bool] = None) -> list[SimMachine]:
        machines = [self._instance.machines[machine_id]
                    for machine_id in self._instance.operation_machines[operation_id]]
        return list(filter(machine_filter, machines)) if machine_filter else machines

    def get_machine_operations(self, machine_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id]
                for operation_id in self._instance.operation_machines[machine_id]]

    def get_operation_predecessors(self, operation_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id]
                for operation_id in self._instance.operation_relations.predecessors(operation_id)]

    def get_operation_successors(self, operation_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id]
                for operation_id in self._instance.operation_relations.successors(operation_id)]

    def get_job_source_operations(self, job_id: UUID) -> list[SimOperation]:
        source_ids = [operation_id for operation_id in self._instance.job_operations[job_id]
                      if self._instance.operation_relations.in_degree(operation_id) == 0]
        return [self._instance.operations[source_id] for source_id in source_ids]

    def get_all_source_operations(self, source_filter: Callable[[SimOperation], bool] = None) -> list[SimOperation]:
        source_ids = [operation_id for operation_id in self._instance.operation_relations
                      if self._instance.operation_relations.in_degree(operation_id) == 0]
        source_operations = [self._instance.operations[source_id] for source_id in source_ids]
        return list(filter(source_filter, source_operations)) if source_filter else source_operations
