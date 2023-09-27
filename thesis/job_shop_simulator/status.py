from typing import Callable

from .sim_component import *


class Status:
    def __init__(self, instance):
        self._instance = instance

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

    def get_job_operations(self, job_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id] for operation_id in self._instance.job_operations[job_id]]

    def get_job_operations_raw(self, job_id: UUID) -> list[Operation]:
        raw_job_id = self._instance.jobs[job_id].raw.id
        return [self._instance.config.operations[raw_operation_id]
                for raw_operation_id in self._instance.config.job_operations[raw_job_id]]

    def get_operation_job(self, operation_id: UUID) -> SimJob:
        return [self._instance.jobs[job_id] for job_id in self._instance.job_operations[operation_id]][0]

    def get_operation_machines(self, operation_id: UUID) -> list[SimMachine]:
        return [self._instance.machines[machine_id] for machine_id in self._instance.operation_machines[operation_id]]

    def get_machine_operations(self, machine_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id]
                for operation_id in self._instance.operation_machines[machine_id]]

    def get_operation_predecessors(self, operation_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id]
                for operation_id in self._instance.operation_relations.predecessors(operation_id)]

    def get_operation_successors(self, operation_id: UUID) -> list[SimOperation]:
        return [self._instance.operations[operation_id]
                for operation_id in self._instance.operation_relations.successors(operation_id)]


    def set_operation_relations_level(self, job_id: UUID, operation_relations:DiGraph):
        # Returns the level of the operation relations.
        sim_Operation = self.get_job_source_operations(job_id)[0]
        i = 0
        while True:
            sim_Operation.set_attribute('Level', i)
            i += 1
            if operation_relations.successors(sim_Operation.id):
                sim_Operation = self.get_operation_successors(sim_Operation.id)[0]
            else:
                break

    def get_job_source_operations(self, job_id: UUID) -> list[SimOperation]:
        print("这是",self.job_raw(job_id).id)
        source_ids = [operation_id for operation_id in self._instance.job_operations[job_id]
                      if self._instance.operation_relations.in_degree(operation_id) == 0]
        print("source_ids",source_ids)
        for sourceOperation_id in source_ids:
            print(self.operation_raw(sourceOperation_id).id)
            """a = self._instance.operations[source_id]
            print(self.operation_raw(a).id)"""
        print("____get_job_source_operations_______")
        return [self._instance.operations[source_id] for source_id in source_ids]

    def get_all_source_operations(self) -> list[SimOperation]:
        source_ids = [operation_id for operation_id in self._instance.operation_relations
                      if self._instance.operation_relations.in_degree(operation_id) == 0]
        return [self._instance.operations[source_id] for source_id in source_ids]

    def get_filter_machine(self, operation_id: UUID, machine_filter: Callable[[SimMachine], bool]) -> list[SimMachine]:
        #fliter函数，只保留能让machine_filter为true的machine
        return list(filter(machine_filter, [self._instance.machines[machine_id]
                                            for machine_id in self._instance.operation_machines[operation_id]]))
