class MachineData:
    def __init__(self):
        # 初始化所有的数据为0或空列表，具体的初始化可以根据实际情况进行调整
        self.operations_queue = []  # 机器队列中的操作列表
        self.work_in_queue = []     # 机器队列中的工作列表
        self.waiting_time = 0       # 机器的等待时间
        self.processing_time = {}   # 操作在给定机器上的处理时间
        self.next_operation_pt = [] # 下一个操作的中位处理时间列表
        self.operation_waiting_time = {} # 操作的等待时间
        self.remaining_work_for_job = {} # 作业剩余的工作量
        self.remaining_operations_in_job = {} # 作业中剩余的操作数
        self.job_weight = {}        # 作业的权重
        self.time_in_system = 0     # 系统中的时间

    def NIQ(self):
        return len(self.operations_queue)

    def WIQ(self):
        return len(self.work_in_queue)

    def MWT(self):
        return self.waiting_time

    def PT(self, operation):
        return self.processing_time.get(operation, 0)

    def NPT(self):
        # 获取中位数处理时间
        sorted_times = sorted(self.next_operation_pt)
        length = len(sorted_times)
        if length % 2 == 0:
            return (sorted_times[length // 2 - 1] + sorted_times[length // 2]) / 2
        return sorted_times[length // 2]

    def OWT(self, operation):
        return self.operation_waiting_time.get(operation, 0)

    def WKR(self, job_id):
        return self.remaining_work_for_job.get(job_id, 0)

    def NOR(self, job_id):
        return self.remaining_operations_in_job.get(job_id, 0)

    def W(self, job_id):
        return self.job_weight.get(job_id, 0)

    def TIS(self):
        return self.time_in_system
