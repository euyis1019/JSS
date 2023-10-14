import random

import numpy.random

from thesis.job_shop_simulator import *

generator = numpy.random.default_rng(42)


def get_inter_arrival_time_mean(machine_num, operations_min, operations_max, process_min, process_max, util_level):
    mean_operations = 0.5 * (operations_min + operations_max)
    mean_process = 0.5 * (process_min + process_max)
    return (mean_operations * mean_process) / (util_level * machine_num)


def get_random_config(job_num, operations_min, operations_max, machine_num, process_min, process_max,
                      util_level) -> Config:
    """
    :param job_num: number of jobs
    :param operations_min: min operations
    :param operations_max: max operations
    :param machine_num: number of machines
    :param process_min: min process time
    :param process_max: max process time
    :param util_level: utilization level
    :return: random config
    """
    random.seed(44)
    inter_arrival_time_mean = get_inter_arrival_time_mean(machine_num, operations_min, operations_max,
                                                          process_min, process_max, util_level)

    machines = dict()
    for i in range(machine_num):
        machine = Machine(uuid.uuid1())
        machines[machine.id] = machine

    jobs = []
    operations = []
    job_operations = []
    operation_relations = []
    operation_machines = []
    arrive_time = 0
    for i in range(job_num):
        arrive_time += generator.exponential(inter_arrival_time_mean)
        job = Job(uuid.uuid1(), {"arrive_time": arrive_time})
        operation_num = random.randint(operations_min, operations_max)
        for j in range(operation_num):
            operation = Operation(uuid.uuid1())
            job_operations.append(JobOperation(job.id, operation.id))
            if j != 0:
                operation_relations.append(OperationRelation(operations[-1].id, operation.id))
            machine_ids = random.sample(list(machines.keys()), random.randint(1, machine_num))
            operation_machines.extend(OperationMachine(operation.id, machine_id,
                                                       {"process_time": random.uniform(1, 10)})
                                      for machine_id in machine_ids)
            operations.append(operation)
        jobs.append(job)

    return Config(jobs, operations, list(machines.values()), job_operations, operation_relations, operation_machines)
