'''
Outils permettant de simplifier et clarifier la vérification des
données entrantes et la sérialisation des données sortantes
'''
# TODO ajouter champs adéquats pour les relations


import datetime
from collections import OrderedDict


def prepare_serial(val):
    '''
    Retourne int ou None pour int serial/autoincrement
    '''
    if val == '':
        return None
    return int(val)


def prepare_date(data):
    '''
    Transforme une chaine de date en objet datetime
    '''
    if not data:
        return None
    if isinstance(data, datetime.datetime):
        return data
    try:
        return datetime.datetime.strptime(data, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            return datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')

def serialize_date(data):
    '''
    retourne une date sous forme de chaine
    '''
    return str(data) if data else None


class Field:
    '''
    Attribute class
    Représente un attribut du modele à serialiser
    '''
    def __init__(
            self,
            *,
            alias=None,
            checkfn=lambda x: True,
            preparefn=lambda x: x,
            serializefn=lambda x: x,
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
        self.default = default

        # indique que la valeur est en lecture seule et qu'elle n'a pas à être passée 
        # à l'instance DB
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
                value = self.preparefn(value)
                if not self.checkfn(value):
                    raise ValueError
                setattr(instance.obj, self.alias or self.name, value)
            except Exception:
                instance.errors[self.name] = value
                raise ValueError

    def __get__(self, instance, owner):
        '''
        Retourne la valeur transformée par 'serializefn'
        '''
        if instance is None:
            return self
        val = getattr(instance.obj, self.alias or self.name, self.default)
        return self.serializefn(val)


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
    affecte le nom de la variable déclarée dans la classe à la class attribut correspondante
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

    def populate(self, data):
        '''
        "Peuple" un objet en passant par les attribute class Field
        et les méthodes de transformation/vérification associées
        '''
        errors = False
        for name, value in data.items():
            try:
                setattr(self, name, value)
            except ValueError as err:  # noqa
                errors = True
                self.errors[name] = value
        if errors:
            raise ValidationError(self.errors)

    def serialize(self, fields=None):
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
                out[field] = getattr(self, field, None)
            return out

    @classmethod
    def export_csv(cls, data, *, fields=None, sep=',', delimiter='"', eol='\n'):
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
            lines.append(sep.join([f_template % (_formatters[f](getattr(item, f, '')) or '') for f in _fields]))
        return eol.join(lines).encode('latin1', 'replace')

