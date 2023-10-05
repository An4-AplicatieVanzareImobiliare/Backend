#imports 1 by 1:
import json
from flask import Flask, request, abort, jsonify, session
#Clasa db:
from models import db, User, Vanzari, Programare
#Configuratii:
from config import AppConfig
from flask_bcrypt import Bcrypt
#Pentru session:
from flask_session import Session
#Pentru legatura FE cu BE, CORS fix + cross origin:
from flask_cors import CORS, cross_origin
#Pentru local time:
from datetime import datetime, timedelta #Primul nu este bun;


#App:
app = Flask(__name__)

#For config:
app.config.from_object(AppConfig)

#Criptare:
bcrypt = Bcrypt(app)

#Pentru cors:
#cors = CORS(app)
#Daca vrem credentiale:
#cors = CORS(app, supports_credentials = True)
cors = CORS(app)

#Pentru sesiune:
#Session din flask nu este la fel de sigur;
server_session = Session(app)

#Init app:
db.init_app(app)

#Create all:
with app.app_context():

    db.create_all()
    # db.drop_all()

    # Not working:
    # db.drop_table(Vanzari)
    # db.drop_table(Programare)
    # Vanzari.__table__.drop(db)

    # Working:
    # Vanzari.__table__.drop(db.engine)
    # Programare.__table__.drop(db.engine)


# GetUserData / Register / Login;




# De la tema 2:



#1) Get User Data:
@cross_origin
@app.route("/userData", methods = ["GET"])
def user_data():

    #User id for user din session:
    #If invalid session, this will return None;
    user_id = session.get("user_id")

    #Daca nu este user id:
    if not user_id:
        return jsonify({"error": "No user id found!"}), 404
    
    #User filtrat by id:
    user_session = User.query.filter_by(id = user_id).first()

    #Return user_exists sub forma de json:
    #Returneaza doar daca este deschis session!!!
    return jsonify({
        "id": user_session.id,
        "email": user_session.email,
        "name": user_session.name,
        "role": user_session.role
    })






#2) Register:
#Pentru rute:
#Request standard email + pass:
#De la locat host 5000 - register:
#Ruta apeleaza metoda definita sub!!! :
#Post method:
@cross_origin
@app.route("/userRegister", methods = ["POST"])
def register_user():

    #Request what you need (parametrii)
    name = request.json["name"]
    email = request.json["email"]
    password = request.json["password"]

    #Daca user exista cu email anume, luam first din rezultat, unique:
    user_exists = User.query.filter_by(email = email).first() is not None

    #Conflict status code:
    #Daca exista deja acest email, trimiti status conflict:
    if user_exists:
        #abort(409) #Fara "";
        return jsonify({"error": "This email is already in use!"}), 409

    #Parola criptata pentru bd:
    hash_pass = bcrypt.generate_password_hash(password)
    #Daca nu exista email, creare nou user cu email + parola:
    #Entitatea user pe care o salvezi in BD;
    #Automat rolul de client:
    new_user = User(name = name, email = email, 
                    role = "client", password = hash_pass) #client or admin

    #In real time BD:
    #Pentru sesiune, add user + commit:
    #Add in DB:
    db.session.add(new_user)
    db.session.commit()


    #Dupa register si add user, deschizi o sesiune pentru noul user:
    session["user_id"] = new_user.id


    #Return new user json format: (fara parola, doar id + email)
    return jsonify({
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name,
        "role": new_user.role
    })






#3) Login:
@cross_origin
@app.route("/userLogin", methods = ["POST"])
def login_user():
    
     #Request what you need (parametrii)
    email = request.json["email"]
    password = request.json["password"]

    #Daca user exista cu email anume, luam first din rezultat, unique:
    user_exists = User.query.filter_by(email = email).first()

    #Daca nu exista email:
    if user_exists is None:
        return jsonify({"error": "This email is not in our data base!"}), 404

    #User exists: Check password: Daca nu este check:
    if not bcrypt.check_password_hash(user_exists.password, password):
        return jsonify({"error": "The password is not correct!"}), 401
    


    #Stocare date in sesiune (pentru cand user-ul se logeaza!!!):
    #Store data in session, user id:
    #Value din cookies este session id; (Se salveaza in cookie)
    session["user_id"] = user_exists.id


    
    #Return logied in user:
    #return user_exists sub forma de json:
    return jsonify({
        "id": user_exists.id,
        "email": user_exists.email,
        "name": user_exists.name,
        "role": user_exists.role
    })






#4)Logout:
@cross_origin
@app.route("/userLogout", methods = ["POST"])
def logout_user():

    #Scos din sesiunea curenta user id:
    #session.pop["user_id"]

    #Nu merge:
    #session.pop["user_id"]

    #Return ok:
    return "200"






#5) Get Vanzari Data:
@cross_origin
@app.route("/vanzariData", methods = ["GET"])
def vanzari_data():

    #All vanzari: Lista simpla:
    #all_vanzari = db.Vanzari.query.filter_by().all()
    #all_vanzari = db.Vanzari.query.filter_by().all()
    #Not db here:
    all_vanzari = Vanzari.query.all()

    #Nu se primeste nimic, se da lista goala daca nu sunt date;

    #Prelucrare lista:
    #all_vanzari_list = json.dumps(Vanzari.serialize_list(all_vanzari)
    #all_vanzari_list = [d.__dict__ for d in all_vanzari]

    #Return all: Toata lista deodata:
    #return jsonify({
    #    "all_vanzari_list" : all_vanzari_list,
        ##status=200, 
        ##mimetype='application/json'
    #    })
    #return all_vanzari_list
    #return jsonify(result = all_vanzari_list)

    #Return cu json dumps serializarea in lista:
    #1)
    #return json.dumps(Vanzari.serialize_list(all_vanzari))
    #2) Not Array?
    #return jsonify(vanzari_list = Vanzari.serialize_list(all_vanzari))
    #3) Array cu jsonify:
    return jsonify(Vanzari.serialize_list(all_vanzari))





#6) Add Vanzari:
@cross_origin
@app.route("/vanzariAdd", methods = ["POST"])
def vanzari_add():    

    #Cer toate campurile inafara de id:
    metriPatrati = request.json["metriPatrati"]
    numarCamere = request.json["numarCamere"]
    locatie = request.json["locatie"]
    pret = request.json["pret"]
    tip = request.json["tip"]

    #Daca locatia exista deja, nu se pune: Unique kinda:
    vanzare_exists = Vanzari.query.filter_by(locatie = locatie).first() is not None

    #If exists:
    if vanzare_exists:
        return jsonify({"error": "This sale is already there!"}), 409

    #Creare vanzare:
    new_vanzare = Vanzari(metriPatrati = metriPatrati,
                          numarCamere = numarCamere,
                          locatie = locatie, #Not string!
                          pret = pret,
                          tip = tip)

    #Add to db: Session:
    db.session.add(new_vanzare)
    db.session.commit()

    #Return the sale:
    return jsonify({
        "id": new_vanzare.id,
        "metriPatrati": new_vanzare.metriPatrati,
        "numarCamere": new_vanzare.numarCamere,
        "locatie": new_vanzare.locatie,
        "pret": new_vanzare.pret,
        "tip": new_vanzare.tip,
    })






#7) Update Vanzari:
@cross_origin
@app.route("/vanzariUpdate", methods = ["POST"])
def vanzari_update():

    #Cer toate campurile inafara de id: (pentru update!)
    metriPatrati = request.json["metriPatrati"]
    numarCamere = request.json["numarCamere"]
    locatie = request.json["locatie"]
    pret = request.json["pret"]
    tip = request.json["tip"]

    #Daca locatia nu exista, nu se poate da update:
    vanzare_exists = Vanzari.query.filter_by(locatie = locatie).first()

    #If not exists, ca e null, sau none:
    if vanzare_exists is None:
        return jsonify({"error": "This sale is not there!"}), 404

    #Update and commit: Returnare numar de rows updated;
    # rows_updated = vanzare_exists.update(dict(
    #                                           id = vanzare_exists.id,
    #                                           metriPatrati = metriPatrati,
    #                                           numarCamere = numarCamere,
    #                                           locatie = locatie,
    #                                           pret = pret,
    #                                           tip = tip)
    #                                           )
    #Doar schimbi si dai commit, ca un save implicit:      
    # db.session.add(vanzare_exists)

    #Schimb pe rand toate fieldurile inafara de id, si dupa dau commit:
    vanzare_exists.metriPatrati = metriPatrati
    vanzare_exists.numarCamere = numarCamere
    vanzare_exists.locatie = locatie
    vanzare_exists.pret = pret
    vanzare_exists.tip = tip
    db.session.commit()

    #Return la ce este acum:
    return jsonify({
        "id": vanzare_exists.id,
        "metriPatrati": vanzare_exists.metriPatrati,
        "numarCamere": vanzare_exists.numarCamere,
        "locatie": vanzare_exists.locatie,
        "pret": vanzare_exists.pret,
        "tip": vanzare_exists.tip,
    })





#8) Delete Vanzari:
@cross_origin
@app.route("/vanzariDelete", methods = ["POST"])
def vanzari_delete():                

    #Cer locatie:
    locatie = request.json["locatie"]

    #Daca locatia nu exista, nu se poate da delete:
    vanzare_exists = Vanzari.query.filter_by(locatie = locatie).first()
    old_vanzare = vanzare_exists #Copy;

    #If not exists, ca e null, sau none:
    if vanzare_exists is None:
        return jsonify({"error": "This sale is not there!"}), 404

    #Daca exista, se sterge si se returneaza cea veche:
    db.session.delete(vanzare_exists)
    db.session.commit()

    #Return la ce era:
    return jsonify({
        "id": old_vanzare.id,
        "metriPatrati": old_vanzare.metriPatrati,
        "numarCamere": old_vanzare.numarCamere,
        "locatie": old_vanzare.locatie,
        "pret": old_vanzare.pret,
        "tip": old_vanzare.tip,
    })





# De la tema 3:




#9) Insert programare de catre user:
@cross_origin
@app.route("/programareAdd", methods = ["POST"])
def addProgramare():    



    #Ce primesti:
    #Imobil data: (+ id)
    # imobil_id = request.json["imobil_id"]
    imobil_metriPatrati = request.json["imobil_metriPatrati"]
    imobil_numarCamere = request.json["imobil_numarCamere"]
    imobil_locatie = request.json["imobil_locatie"]
    imobil_pret = request.json["imobil_pret"]
    imobil_tip = request.json["imobil_tip"]

    #Date and Time:
    #String si Integer stiu sa primeasca direct, DateTime nu:
    
    #Basic este string:
    #date_and_time = request.json["date_and_time"]
    date_and_time_string = request.json["date_and_time_string"]
    #Convertire: din string in date time: Pun T sa fie ca la react:
    date_and_time = datetime.strptime(date_and_time_string, "%Y-%m-%dT%H:%M:%S")

    #User email se primeste:
    user_email = request.json["user_email"]

    #Get user id: Nu poate da fail, se ia tot timpul un email corect!!!
    user_id = User.query.filter_by(email = user_email).first().id

    #Get imobil id by locatie:
    imobil_id = Vanzari.query.filter_by(locatie = imobil_locatie).first().id


    #Filter bool by imobil_id and date_and_time:
    programari_exists = Programare.query.filter_by(imobil_id = imobil_id, date_and_time = date_and_time).first() is not None

    #Daca exista deja:
    if programari_exists:

        #1)
        # return jsonify({"error": "This sale is already there!"}), 409
        
        #2)
        # Pentru conflict, logica de cautare a unei ore in functie de cea data:

        # Noua data trimisa ca recomandare: 
        date_and_time_recomandation = date_and_time

        # Get data:
        # year = date_and_time.year
        # month = date_and_time.month
        # day = date_and_time.day
        # hour = date_and_time.hour

        # Compare cu ce este in BD, fata de noul timp: Incepe de la 1!
        newHour = 1

        # Verific daca se incadreaza:
        # if date_and_time.hour + newHour > 23 or date_and_time.hour - newHour < 0:
        #         return jsonify({"error": "No more spots for today!"}), 409

        # Verific in fata:
        # date_and_time_recomandation.replace(hour = date_and_time.hour + newHour) #Replace nu merge;
        # Alt format, dar doar pentru alert este folosit:
        date_and_time_recomandation = date_and_time + timedelta(hours = newHour)
        print("Test for hour: ", date_and_time.hour + newHour, " !")
        print("New date replaced: ", date_and_time_recomandation)

        # First try:
        programari_exists_recomandation = Programare.query.filter_by(imobil_id = imobil_id, date_and_time = date_and_time_recomandation).first() is not None

        # Daca exista, testez si in spate:
        if programari_exists_recomandation:

            # date_and_time_recomandation.replace(hour = date_and_time.hour - newHour)
            date_and_time_recomandation = date_and_time - timedelta(hours = newHour)
            print("Test for hour: ", date_and_time.hour - newHour, " !")

            programari_exists_recomandation = Programare.query.filter_by(imobil_id = imobil_id, date_and_time = date_and_time_recomandation).first() is not None


        # Cat timp exista recomandarea, mai caut:
        # De mai sus, daca nici - nu merge, testez ambele:
        while programari_exists_recomandation:

            # Higher + Lower;
            newHour = newHour + 1

            # Test for new hour: Not writable: Deci replace, cu +:

            # Daca nu mai sunt ore:
            # if date_and_time.hour + newHour > 23 or date_and_time.hour - newHour < 0:
            #     return jsonify({"error": "No more spots for today!"}), 409

            # Test ora inainte:
            # date_and_time_recomandation.replace(hour = date_and_time.hour + newHour)
            date_and_time_recomandation = date_and_time + timedelta(hours = newHour)
            print("Test for hour: ", date_and_time.hour + newHour, " !") # Merge din 1 in 1!

            programari_exists_recomandation = Programare.query.filter_by(imobil_id = imobil_id, date_and_time = date_and_time_recomandation).first() is not None

            # Daca exista, incerc urmatoarea:
            if programari_exists_recomandation:
                
                #date_and_time_recomandation.replace(hour = date_and_time.hour - newHour)
                date_and_time_recomandation = date_and_time - timedelta(hours = newHour)
                print("Test for hour: ", date_and_time.hour - newHour, " !") # Merge din 1 in 1!

                programari_exists_recomandation = Programare.query.filter_by(imobil_id = imobil_id, date_and_time = date_and_time_recomandation).first() is not None



        # Returnez un obiect cu data noua, si restul datelor null:
        return jsonify({
            "imobil_id": "",
            "imobil_metriPatrati": 0,
            "imobil_numarCamere": 0,
            "imobil_locatie": "",
            "imobil_pret": 0,
            "imobil_tip": "",

            #Date and time:
            "date_and_time": date_and_time_recomandation,

            #User id:
            "user_id": "",
        }) #, 409


    #Daca nu exista, inserat in BD:
    new_programare = Programare(
                          #Imobil data:
                          imobil_id = imobil_id,
                          imobil_metriPatrati = imobil_metriPatrati,
                          imobil_numarCamere = imobil_numarCamere,
                          imobil_locatie = imobil_locatie, #Not string!
                          imobil_pret = imobil_pret,
                          imobil_tip = imobil_tip,
                          
                          #Date and time:
                          date_and_time = date_and_time,  

                          #User id:
                          user_id = user_id
                          )

    #Add in db:
    db.session.add(new_programare)
    db.session.commit()



    #Nu return status daca este bine;
    #Return the object:
    return jsonify({
        #Imobil Data:
        "imobil_id": new_programare.imobil_id,
        "imobil_metriPatrati": new_programare.imobil_metriPatrati,
        "imobil_numarCamere": new_programare.imobil_numarCamere,
        "imobil_locatie": new_programare.imobil_locatie,
        "imobil_pret": new_programare.imobil_pret,
        "imobil_tip": new_programare.imobil_tip,

        #Date and time:
        "date_and_time": new_programare.date_and_time,

        #User id:
        "user_id": new_programare.user_id,
    }) #, 200
    #As putea 201 dar pun 200 pentru siguranta!!!





#10) Get all programari de la un imobil;
#<string:arg1>;
@cross_origin
@app.route("/getAllProgramariForImobil/<imobil_locatie>", methods = ["GET"])
def getAllProgramariForImobil(imobil_locatie):

    #Luat luna curenta: Si anul curent:
    year = datetime.now().year #Always 2023;
    month = datetime.now().month #Si luna este importanta pentru fe;

    #Pentru test, luna 5 + 3 = 8; (August!)
    month = month + 0 # 1 si 3;
    #print("Luna: ", month)

    #Get all from query: In functie de locatie si de luna anume:
    all_programari_imobil = Programare.query.filter_by(imobil_locatie = imobil_locatie)
    
    #Daca nu exista, va fi lista goala:
    #Pana la final:
    all_programari = []
      
    #Acum filtrez in functie de luna:
    for programare in all_programari_imobil:

        #Daca luna este aceeasi, o voi adauga: Verific si anul:
        if programare.date_and_time.month == month and programare.date_and_time.year == year:
            all_programari.append(programare)

    #Return lista la final:
    return jsonify(Programare.serialize_list(all_programari))




#11) Delete programare:
@cross_origin
@app.route("/programareDelete", methods = ["POST"])
def programare_delete():                

    #Cer programare id:
    id = request.json["id"]

    #Daca programarea nu exista, nu se poate da delete:
    programare_exists = Programare.query.filter_by(id = id).first()
    old_programare = programare_exists

    #If not exists, ca e null, sau none:
    if programare_exists is None:
        return jsonify({"error": "This reservation is not there!"}), 404

    #Daca exista, se sterge si se returneaza cea veche:
    db.session.delete(programare_exists)
    db.session.commit()

    #Return la ce era:
    #Return status 200 implicit;
    return jsonify({
        "id": old_programare.id,
        "user_id": old_programare.user_id,
    })




#12) All reservations: for 1 imobil:
@cross_origin
@app.route("/getAllProgramari", methods = ["GET"])
def getAllProgramari():

    #Get all from query: 
    all_programari_imobil = Programare.query.all()
    
    #The list:
    all_programari = []
      
    #Acum filtrez in functie de luna:
    for programare in all_programari_imobil:

        #Daca luna este aceeasi, o voi adauga: Verific si anul:
        if programare.imobil_locatie == "Cluj_Napoca_Cluj8_V":
            all_programari.append(programare)

    #Return lista la final:
    return jsonify(Programare.serialize_list(all_programari))




#Pentru run:
if __name__ == "__main__":
    app.run(debug = True)