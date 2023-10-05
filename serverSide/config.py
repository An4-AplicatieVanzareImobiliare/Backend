from dotenv import load_dotenv
import os
import redis

load_dotenv()

#Different configuration:
class AppConfig:

    #Secret key:
    SECRET_KEY = os.environ["SECRET_KEY"]

    #Nu mai face track la loguri useless;
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = True

    #Regex: Exemplu de db:
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    #Pentru session cu redis:
    SESSION_TYPE = "redis"

    #Sa nu fie permanenta sesiunea:
    SESSION_PERMANENT = False

    #Flag:
    SESSION_SIGNER = True

    #Pentru server redis:
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")
