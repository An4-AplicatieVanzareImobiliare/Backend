from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy.inspection import inspect





#Data Base:
db = SQLAlchemy()

#Get uuid hex: 
#Trebuie deasupra pentru a merge uuid mai jos:
#Default id este uuid pentru fiecare user;
def get_uuid():
    return uuid4().hex





#Clasa serializare:
class Serializer(object):
    def serialize(self):
        return {column: getattr(self, column) for column in inspect(self).attrs.keys()}
    #Pentru serializare:
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
    



# De la tema 2:




#Clasa user:
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.String(32),
                   primary_key = True, 
                   unique = True, 
                   default = get_uuid) #Primary key
    name = db.Column(db.String(300),
                      unique = False)
    email = db.Column(db.String(300),
                      unique = True)
    role = db.Column(db.String(300),
                      unique = False)
    password = db.Column(db.Text,
                         nullable = False)
    




#Clasa vanzari:
#Doar aici trebuie serializare:
class Vanzari(db.Model, Serializer):
    __tablename__ = "Vanzari"
    id = db.Column(db.String(32),
                   primary_key = True, 
                   unique = True, 
                   default = get_uuid) #Primary key
    metriPatrati = db.Column(db.Integer,
                      nullable = False)
    numarCamere = db.Column(db.Integer,
                      nullable = False)
    locatie = db.Column(db.String(300),
                      nullable = False)
    pret = db.Column(db.Integer, #Fara Float;
                         nullable = False)
    tip = db.Column(db.Text,
                         nullable = False)

    #Functie in clasa, pentru serializare:
    #Pentru overide, altfel este destul serializer;
    # def serialize(self):
    #     omis = Serializer.serialize(self)
    #     del omis['id']
    #     return omis





#Clasa inchirieri:
#Nu am facut;




# De la tema 3:



#Clasa programare:
class Programare(db.Model, Serializer):
    __tablename__ = "Programari"

    #Id pentru tabel programari:
    id = db.Column(db.String(32),
                   primary_key = True, 
                   unique = True, 
                   default = get_uuid) 

    #Datele imobilului la care se face programarea:
    #Unique este local doar pentru aceasta tabela;
    imobil_id = db.Column(db.String(32), 
                   unique = False)
    imobil_metriPatrati = db.Column(db.Integer,
                      nullable = False)
    imobil_numarCamere = db.Column(db.Integer,
                      nullable = False)
    imobil_locatie = db.Column(db.String(300),
                      nullable = False)
    imobil_pret = db.Column(db.Integer, #Fara Float;
                         nullable = False)
    imobil_tip = db.Column(db.Text,
                         nullable = False)
    
    #Data + Time: (Time sau DateTime) (Se poate si separat)
    #Trebuie selectata data, altfel nu poti da submit; So no default
    date_and_time = db.Column(db.DateTime(timezone = True),
                         nullable = False)

    #User id:
    user_id = db.Column(db.String(32),
                   unique = False) 