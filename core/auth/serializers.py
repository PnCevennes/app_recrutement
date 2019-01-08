from core.utils.serialize import Serializer, Field, prepare_serial

class UserSerializer(Serializer):
    id = Field(preparefn=prepare_serial)
    name = Field()


class UserFullSerializer(UserSerializer):
    password = Field(serializefn=lambda x: '')
    login = Field()
    email = Field()
    groups = Field(
        serializefn=lambda grps: [grp.name for grp in grps])
