#coding: utf8
'''
Outils permettant de simplifier et clarifier la vérification des
données entrantes et la sérialisation des données sortantes
'''
#TODO ajouter champs adéquats pour les relations


import datetime
from collections import OrderedDict


def prepare_date(data):
    '''
    Transforme une chaine de date en objet datetime
    '''
    if not data: 
        return
    if isinstance(data, datetime.datetime):
        return data
    try:
        return datetime.datetime.strptime(data, '%Y-%m-%d')
    except ValueError:
        return datetime.datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%fZ')


def serializer(cls):
    '''
    Décorateur nécéssaire pour initialiser une classe dérivée de Serializer
    TODO: voir si c'est remplaçable par une metaclasse
    '''
    if not hasattr(cls, '__fields_list__'):
        cls.__fields_list__ = []
    else:
        cls.__fields_list__ = cls.__fields_list__[:]
    for attr, field in cls.__dict__.items():
        if isinstance(field, Field):
            field.name = attr
            cls.__fields_list__.append(attr)
    return cls


class Field:
    '''
    Attribute class
    Représente un attribut du modele à serialiser
    '''
    def __init__(self, *,
            alias=None,
            checkfn=lambda x: True,
            preparefn=lambda x: x,
            serializefn=lambda x: x,
            default=None):
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


    def __set__(self, instance, value):
        '''
        Transmet la valeur fournie a l'objet à "peupler"
        Etape 1 : la valeur est transformée par la fonction 'preparefn'
        (si la transformation échoue, la valeur transmise était incorrecte)
        Etape 2 : le résultat transformé est évalué par la fonction 'checkfn'

        '''
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


class Serializer:
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
            except ValueError as err:
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
        if fields is None :
            return {field: getattr(self, field) for field in self.__fields_list__}
        else:
            out = OrderedDict()
            for field in fields:
                out[field] = getattr(self, field)
            return out


'''
@serializer
class TestSerializer(Serializer):
    #a = Field(serializefn=lambda x: x.strftime('%d/%m/%Y %H-%M-%S'))
    a = Field(serializefn=str)
    b = Field(alias='plop', serializefn=lambda x: x+5, default=10, checkfn=lambda x: 1<=x<=100)
    c = Field()
    d = Field()
'''
