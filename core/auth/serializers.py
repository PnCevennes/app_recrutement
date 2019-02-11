from core.utils.serialize import Serializer, Field, IntField

class UserSerializer(Serializer):
    id = IntField()
    name = Field()


class UserFullSerializer(UserSerializer):
    password = Field(serializefn=lambda x: '')
    login = Field()
    email = Field()
    groups = Field(
        serializefn=lambda grps: [grp.name for grp in grps])
