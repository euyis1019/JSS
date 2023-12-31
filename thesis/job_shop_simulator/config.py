from networkx import Graph, DiGraph

from .entity import *


class Job(Entity):
    def __init__(self, id, attributes: dict = None):
        super().__init__(id, attributes)


class Operation(Entity):
    def __init__(self, id, attributes: dict = None):
        super().__init__(id, attributes)


class Machine(Entity):
    def __init__(self, id, attributes: dict = None):
        super().__init__(id, attributes)


class OperationMachine(Relation):
    def __init__(self, operation_id, machine_id, attributes: dict = None):
        super().__init__(operation_id, machine_id, attributes)


class OperationRelation(Relation):
    def __init__(self, from_operation_id, to_operation_id, attributes: dict = None):
        super().__init__(from_operation_id, to_operation_id, attributes)


class JobOperation(Relation):
    def __init__(self, job_id, operation_id, attributes: dict = None):
        super().__init__(job_id, operation_id, attributes)


class Config:
    def __init__(self,
                 jobs: list[Job],
                 operations: list[Operation],
                 machines: list[Machine],
                 job_operations: list[JobOperation],
                 operation_relations: list[OperationRelation],
                 operation_machines: list[OperationMachine],
                 global_config: Attributes = None):
        self.jobs: dict[object, Job] = dict((job.id, job) for job in jobs)
        self.operations: dict[object, Operation] = dict((operation.id, operation) for operation in operations)
        self.machines: dict[object, Machine] = dict((machine.id, machine) for machine in machines)

        self.job_operations: Graph = Graph()
        for job_operation in job_operations:
            self.job_operations.add_edge(job_operation.l_id, job_operation.r_id, raw=job_operation)

        self.operation_relations: DiGraph = DiGraph()
        for operation in self.operations.values():
            self.operation_relations.add_node(operation.id)
        for operation_relation in operation_relations:
            self.operation_relations.add_edge(operation_relation.l_id,
                                              operation_relation.r_id,
                                              raw=operation_relation)

        self.operation_machines: Graph = Graph()
        for operation_machine in operation_machines:
            self.operation_machines.add_edge(operation_machine.l_id,
                                             operation_machine.r_id,
                                             raw=operation_machine)

        self.global_config: Attributes = global_config

    def sub_config(self, job_ids: list):
        jobs = []
        operations = []
        machines = list(self.machines.values())
        job_operations = []
        operation_relations = []
        operations_machines = []
        for job_id in job_ids:
            jobs.append(self.jobs[job_id])
            for operation_id, attrs in self.job_operations[job_id].items():
                operations.append(self.operations[operation_id])
                job_operations.append(attrs["raw"])
                for s_operation_id, attrs in self.operation_relations[operation_id].items():
                    operation_relations.append(attrs["raw"])
                for machine_id, attrs in self.operation_machines[operation_id].items():
                    operations_machines.append(attrs["raw"])
        return Config(jobs, operations, machines, job_operations, operation_relations, operations_machines)
