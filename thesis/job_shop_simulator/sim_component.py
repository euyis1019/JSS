from .config import *
from .entity import *


class SimComponent:
    def __init__(self, raw: Entity or Relation):
        self.raw: Entity or Relation = raw


class SimEntity(SimComponent, UEntity):
    def __init__(self, raw: Entity):
        super().__init__(raw)
        super(SimComponent, self).__init__()


class SimRelation(SimComponent, URelation):
    def __init__(self, l_id: UUID, r_id: UUID, raw: Relation):
        super().__init__(raw)
        super(SimComponent, self).__init__(l_id, r_id)


class SimJob(SimEntity):
    def __init__(self, raw: Job):
        super().__init__(raw)


class SimOperation(SimEntity):
    def __init__(self, raw: Operation):
        super().__init__(raw)


class SimMachine(SimEntity):
    def __init__(self, raw: Machine):
        super().__init__(raw)


class SimJobOperation(SimRelation):
    def __init__(self, l_id: UUID, r_id: UUID, raw: JobOperation):
        super().__init__(l_id, r_id, raw)


class SimOperationMachine(SimRelation):
    def __init__(self, l_id: UUID, r_id: UUID, raw: OperationMachine):
        super().__init__(l_id, r_id, raw)


class SimOperationRelation(SimRelation):
    def __init__(self, l_id: UUID, r_id: UUID, raw: OperationRelation):
        super().__init__(l_id, r_id, raw)
