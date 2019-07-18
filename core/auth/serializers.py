from core.utils.serialize import (
    Serializer,
    Field,
    IntField,
    PasswordField,
    MultipleField
)


class UserSerializer(Serializer):
    id = IntField()
    name = Field()


class UserFullSerializer(UserSerializer):
    password = PasswordField(serializefn=lambda x: '')
    login = Field()
    email = Field()
    groups = MultipleField(
        serializefn=lambda grps: [grp.name for grp in grps])
