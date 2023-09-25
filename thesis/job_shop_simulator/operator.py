from collections import namedtuple
from uuid import UUID

from simpy.core import SimTime

Arrangement = namedtuple("Arrangement", ["machine_id", "operation_time"])

#比instance的等级更高
class Operator:
    def __init__(self, instance):
        self._instance = instance

    def arrange_machine(self, machine_id: UUID, operation_time: SimTime):
        self._instance.arrangements.put(Arrangement(machine_id, operation_time))

    def clear_machine_arrangements(self, machine_id: UUID):
        arrangements = [item for item in self._instance.arrangements.items if item.machine_id == machine_id]
        for arrangement in arrangements:
            self._instance.arrangements.items.remove(arrangement)

    def delete_job(self, job_id: UUID):
        operation_ids = self._instance.job_operations[job_id]
        for operation_id in operation_ids:
            self.delete_operation(operation_id)
        self._instance.job_operations.remove_node(job_id)
        del self._instance.jobs[job_id]

    def delete_operation(self, operation_id: UUID):
        #删除与该操作相连的job、operations、machines
        self._instance.operation_machines.remove_node(operation_id)
        self._instance.operation_relations.remove_node(operation_id)
        self._instance.job_operations.remove_node(operation_id)
        del self._instance.operations[operation_id]
