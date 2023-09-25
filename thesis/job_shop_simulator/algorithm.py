from uuid import UUID

from simpy.core import SimTime

from .config import Job, Machine
from .sim_component import SimMachine


class Algorithm:
    """
    the class needs to be inherited
    """

    def on_operation_finished(self, machine_id: UUID, status, operator) -> None:
        """
        the func is called when an operation is finished
        :param operator: the operator of sim environment
        :param status: the status of sim environment
        :param machine_id: the finish operation machine
        """
        pass

    def on_job_arrived(self, job_id: UUID, status, operator) -> None:
        """
        the func is called when a new job is arrived
        :param operator: the operator of sim environment
        :param status: the status of sim environment
        :param job_id: the arrived job
        """
        pass

    def on_machine_offline(self, machine_id: UUID, status, operator) -> None:
        """
        the func is called when a machine offline
        :param operator: the operator of sim environment
        :param status: the status of sim environment
        :param machine_id: the offline machine
        """
        pass

    def on_machine_online(self, machine_id: UUID, status, operator) -> None:
        """
        the func is called when a machine has recovered from offline
        :param operator: the operator of sim environment
        :param status: the status of sim environment
        :param machine_id: the recovered machine
        """
        pass

    def on_decide_job_arrive_time(self, job: Job) -> SimTime:
        """
        the func is called when need to decide job arrive time
        :param job: the job will arrive
        :return the time job will arrive
        """
        pass

    def on_decide_machine_offline_time(self, machine: Machine) -> list[tuple[SimTime, SimTime]]:
        """
        the func is called when need to decide when the machine offline
        :param machine: the machine may offline
        :return machine offline time list, each element has two SimTimes
                indicating the start time and end time of offline.
                The elements are not intersected with each other.
        """
        return []

    def on_init_machine(self, machine: SimMachine) -> None:
        """
        the func is called when need to initialize machine
        :param machine: the initialized machine
        """
        pass
