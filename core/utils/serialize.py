'''
Outils permettant de simplifier et clarifier la vérification des
données entrantes et la sérialisation des données sortantes
'''
# TODO ajouter champs adéquats pour les relations


import datetime
from collections import OrderedDict


def format_phone(tel):
    '''
    formate un numéro de téléphone
    '''
    try:
        tel = (
            tel.replace(' ', '')
            .replace('.', '')
            .replace('/', '')
            .replace('-', '')
        )
        return ' '.join(str(a) + str(b) for a, b in zip(
            [x for x in tel[::2]],
            [y for y in tel[1::2]]))
    except Exception:
        return tel


def load_ref(db, klass, attr=None):
    '''
    Lie un objet ou un champ externe
    '''
    def _load_ref(x):
        if x is None:
            return ''
        obj = db.session.query(klass).get(x)
        if not obj:
            return ''
        if attr is None:
            return obj
        return getattr(obj, attr, '')
    return _load_ref


class Field:
    '''
    Attribute class
    Représente un attribut du modele à serialiser
    '''
    def __init__(
            self,
            *,
            alias=None,
            checkfn=None,
            preparefn=None,
            serializefn=None,
            default=None,
            readonly=False):
        '''
        Constructeur
        params (obligatoirement nommés) :
            checkfn : fonction de vérification - doit renvoyer booleen
            preparefn : fonction de transformation en vue de l'insertion
            serializefn : fonction de transformation pour la serialisation
            default : valeur par défaut lors de la serialisation
        '''

        # Nom de l'attribut automatiquement défini par le decorateur serializer
        self.name = None

        # Nom correspondant dans l'objet cible si besoin
        self.alias = alias

        # callback de transformation de la donnée pour la sérialisation
        self.serializefn = serializefn

        # callback de transformation de la donnée pour l'ajout au modèle
        self.preparefn = preparefn

        # callback de vérification de la validité de la donnée
        self.checkfn = checkfn

        # valeur par défaut de l'attribut lors de la sérialisation uniquement
        if default:
            self.default = default
        else:
            self.default = self.init_default

        # indique que la valeur est en lecture seule et qu'elle n'a pas à être
        # passée à l'instance DB
        self.ro = readonly

    def __set__(self, instance, value):
        '''
        Transmet la valeur fournie a l'objet à "peupler"
        Etape 1 : la valeur est transformée par la fonction 'preparefn'
        (si la transformation échoue, la valeur transmise était incorrecte)
        Etape 2 : le résultat transformé est évalué par la fonction 'checkfn'

        '''
        if not self.ro:
            try:
                # Vérification de la donnée
                if self.checkfn:
                    if not self.checkfn(value):
                        raise ValueError
                else:
                    if not self.check(value):
                        raise ValueError

                # Préparation de la donnée
                if self.preparefn:
                    value = self.preparefn(value)
                else:
                    value = self.prepare(value)

                # Vérification de changement
                old_value = getattr(
                    instance.obj,
                    self.alias or self.name,
                    None
                )
                # Enregistrement en cas de changement
                if old_value != value:
                    instance.changed(self.alias or self.name, old_value)
                setattr(instance.obj, self.alias or self.name, value)
            except Exception as exc:
                instance.errors[self.name] = value
                raise ValueError

    def __get__(self, instance, owner):
        '''
        Retourne la valeur transformée par 'serializefn'
        '''
        if instance is None:
            return self
        val = getattr(instance.obj, self.alias or self.name, self.default)
        if self.serializefn:
            return self.serializefn(val)
        else:
            return self.serialize(val)

    @property
    def init_default(self):
        return None

    def check(self, value):
        '''
        Vérification de la validité de la donnée (defaut)
        '''
        return True

    def prepare(self, value):
        '''
        Préparation de la donnée avant la restitution (defaut)
        '''
        return value

    def serialize(self, value):
        '''
        Préparation de la donnée pour l'export en dict
        '''
        return value


class IntField(Field):
    '''
    Attribute class
    Représente un attribut de type Int à serialiser
    '''
    def prepare(self, value):
        if value is None:
            return None
        return int(value)


def defaultPrepareFloat(value):
    '''
    transforme une chaîne en float
    '''
    try:
        if value:
            return float(value)
        return 0
    except ValueError:
        return 0


class FloatField(Field):
    '''
    Attribute class
    Représente un attribut de type Float à serialiser
    '''
    def prepare(self, value):
        if value:
            return float(value)
        return 0

    def serialize(self, value):
        if value:
            return float(value)
        return 0


class DateField(Field):
    '''
    Attribute class
    Représente un attribut de type Date à serialiser
    '''

    def prepare(self, value):
        if not value or not len(value):
            return None
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            return value
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()
            except ValueError:
                return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date()

    def serialize(self, value):
        return str(value) if value else None


class PasswordField(Field):
    '''
    Attribute class
    Représente un attribut de type password à serialiser
    '''
    pass


class MultipleField(Field):
    '''
    Attribute class
    Représente un attribut de type list à serialiser
    '''
    @property
    def init_default(self):
        return []


class FileField(Field):
    '''
    Attribute class
    Représente un attribut de type relation fichier à serialiser
    '''
    @property
    def init_default(self):
        return []

    def serialize(self, value):
        from core.models import FichierSerializer
        if not value:
            return []
        return [FichierSerializer(item).serialize() for item in value]


class ValidationError(Exception):
    '''
    Erreur levée lorsqu'une valeur passée à un attribut est non valide
    '''
    def __init__(self, errors):
        self.errors = errors


class MetaSerializer(type):
    '''
    Metaclass de Serializer
    Ajoute la liste des champs déclarés dans les classes héritant de Serializer
    dans le liste de champs à traiter (__fields_list__)
    affecte le nom de la variable déclarée dans la classe à la class attribut
    correspondante
    '''
    def __new__(cls, name, bases, props):
        props['__fields_list__'] = []
        for parent_class in bases:
            props['__fields_list__'].extend(
                getattr(parent_class, '__fields_list__', []))
        for pname, pfield in props.items():
            if isinstance(pfield, Field):
                pfield.name = pname
                props['__fields_list__'].append(pname)
        return type.__new__(cls, name, bases, props)


class Serializer(metaclass=MetaSerializer):
    '''
    Représentation d'un modele
    '''
    def __init__(self, obj):
        '''
        Initialisé soit avec un objet à serialiser, soit avec
        un objet vide à "peupler"
        '''
        self.obj = obj
        self.errors = {}
        self.changelog = {}

    def changed(self, name, old):
        self.changelog[name] = old

    def load(self, data):
        '''
        "Peuple" un objet en passant par les attribute class Field
        et les méthodes de transformation/vérification associées
        '''
        errors = False
        for name in self.__fields_list__:
            try:
                default_val = getattr(self.__class__, name).default
                value = data.get(name, None)
                if not value:
                    # si le champ n'est pas un mot de passe il est mis a jour
                    # avec la valeur par défaut. si il est de type
                    # PasswordField, il est ignoré
                    if not isinstance(
                        getattr(self.__class__, name),
                        PasswordField
                    ):
                        setattr(self, name, default_val)
                else:
                    setattr(self, name, value)
            except ValueError as err:  # noqa
                errors = True
                self.errors[name] = data.get(name, None)
        if errors:
            raise ValidationError(self.errors)

    def dump(self, fields=None):
        '''
        Sérialise un objet en passant par les attribute class Field
        et les méthodes de transformation associées
        Retourne un dictionnaire.
        Si une liste de champs est fournie, retourne un OrderedDict
        respectant l'ordre de la liste des champs fournis.
        '''
        if fields is None:
            return {field: getattr(self, field)
                    for field in self.__fields_list__}
        else:
            out = OrderedDict()
            for field in fields:
                if isinstance(field, tuple):
                    fname, formatter = field
                    out[fname] = formatter(getattr(self, fname, None))
                else:
                    out[field] = getattr(self, field, None)
            return out

    @classmethod
    def export_csv(
        cls,
        data,
        *,
        fields=None,
        sep=',',
        delimiter='"',
        eol='\n'
    ):
        '''
        Exporte une liste d'objets sous la forme d'un fichier CSV
        '''
        _fields = []
        _formatters = {}

        if fields is None:
            fields = cls.__fields_list__
        for field in fields:
            if isinstance(field, tuple):
                fname, formatter = field
            else:
                fname = field
                formatter = lambda x: x
            _fields.append(fname)
            _formatters[fname] = formatter

        f_template = delimiter + '%s' + delimiter
        lines = [sep.join([f_template % f for f in _fields])]
        for item in data:
            if not isinstance(item, cls):
                item = cls(item)
            lines.append(sep.join([
                f_template % str(
                    _formatters[f](getattr(item, f, '')) or ''
                ).replace('"', '""') for f in _fields
            ]))
        return eol.join(lines).encode('latin1', 'replace')

    # alias pour ancien code
    populate = load
    serialize = dump
