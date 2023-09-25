import uuid
from uuid import UUID


class Id:
    def __init__(self, id):
        self.id = id


class PairId:
    def __init__(self, l_id, r_id):
        self.l_id = l_id
        self.r_id = r_id


class Attributes:
    def __init__(self, attributes: dict = None):
        self.attributes: dict = dict()
        if attributes:
            self.attributes.update(attributes)

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes[key]


class Entity(Id, Attributes):
    def __init__(self, id, attributes: dict = None):
        super().__init__(id)
        super(Id, self).__init__(attributes)


class Relation(PairId, Attributes):
    def __init__(self, l_id, r_id, attributes: dict = None):
        super().__init__(l_id, r_id)
        super(PairId, self).__init__(attributes)


class UEntity(Entity):
    def __init__(self, attributes: dict = None):
        super().__init__(uuid.uuid1(), attributes)


class URelation(Relation):
    def __init__(self, l_id: UUID, r_id: UUID, attributes: dict = None):
        super().__init__(l_id, r_id, attributes)
