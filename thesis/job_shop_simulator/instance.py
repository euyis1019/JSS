from simpy import Environment, FilterStore, Process, Interrupt

from .operator import Operator
from .sim_component import *
from .status import Status


class Instance:
    def __init__(self, config: Config, algorithm):
        self.config: Config = config
        self.algorithm = algorithm
        self._status = Status(self)
        self._operator = Operator(self)
        self.__init__sim_env()

    def __init__sim_env(self):
        self._env: Environment = Environment()
        self.arrangements = FilterStore(self._env)

        self.job_operations: Graph = Graph()
        self.operation_relations: DiGraph = DiGraph()
        self.operation_machines: Graph = Graph()

        self.jobs: dict[UUID, SimJob] = dict()
        self.operations: dict[UUID, SimOperation] = dict()
        self.machines: dict[UUID, SimMachine] = dict()

        self.machine_id_to_sim_id: dict[object, UUID] = dict()

        for machine in self.config.machines.values():
            sim_machine = SimMachine(machine)
            self.machines[sim_machine.id] = sim_machine
            self.machine_id_to_sim_id[machine.id] = sim_machine.id

    def run(self):
        """
        run the simulator instance
        """
        for job in self.config.jobs.values():
            self._env.process(self._run_job(job))
        for sim_machine in self.machines.values():
            sim_machine_process = self._env.process(self._run_machine(sim_machine))
            self._env.process(self._run_machine_offline(sim_machine.raw, sim_machine_process))
        self._env.run()

    def _run_machine_offline(self, machine: Machine, process: Process):
        offline = self.algorithm.on_decide_machine_offline_time(machine)
        offline.sort(key=lambda off: off[0])
        for start, end in offline:
            yield self._env.timeout(start - self._env.now)
            process.interrupt(end - start)

    def _run_machine(self, machine: SimMachine):
        self.algorithm.on_init_machine(machine)
        while True:
            arrangement = yield self.arrangements.get(lambda a: a.machine_id == machine.id)
            try:
                yield self._env.timeout(arrangement.operation_time)
                self.algorithm.on_operation_finished(machine.id, self._status, self._operator)
            except Interrupt as i:
                self.algorithm.on_machine_offline(machine.id, self._status, self._operator)
                yield self._env.timeout(i.cause)
                self.algorithm.on_machine_online(machine.id, self._status, self._operator)

    def _run_job(self, job: Job):
        arrive_time = self.algorithm.on_decide_job_arrive_time(job)
        yield self._env.timeout(arrive_time)
        sim_job = self.__init__job(job)
        self.algorithm.on_job_arrived(sim_job.id, self._status, self._operator)

    def __init__job(self, job: Job) -> SimJob:
        sim_job = SimJob(job)
        self.jobs[sim_job.id] = sim_job

        operation_id_to_sim_id: dict[object, UUID] = dict()
        for job_id, operation_id, raw in self.config.job_operations.edges(job.id, "raw"):
            sim_operation = SimOperation(self.config.operations[operation_id])
            operation_id_to_sim_id[operation_id] = sim_operation.id
            self.operations[sim_operation.id] = sim_operation
            self.job_operations.add_edge(sim_job.id, sim_operation.id,
                                         sim=SimJobOperation(sim_job.id, sim_operation.id, raw))
            for operation_id, machine_id, raw in self.config.operation_machines.edges(operation_id, "raw"):
                sim_machine_id = self.machine_id_to_sim_id[machine_id]
                self.operation_machines.add_edge(sim_operation.id, sim_machine_id,
                                                 sim=SimOperationMachine(sim_operation.id, sim_machine_id, raw))

        operation_ids = list(self.config.job_operations[job.id])
        for from_operation_id, to_operation_id, raw in self.config.operation_relations.edges(operation_ids, "raw"):
            from_sim_id = operation_id_to_sim_id[from_operation_id]
            to_sim_id = operation_id_to_sim_id[to_operation_id]
            self.operation_relations.add_edge(from_sim_id, to_sim_id,
                                              sim=SimOperationRelation(from_sim_id, to_sim_id, raw))
        return sim_job
