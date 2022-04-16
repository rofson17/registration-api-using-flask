from flask import Flask
from flask_pymongo import PyMongo
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os


load_dotenv()

DB = PyMongo()
MAIL = Mail()
BCRYPT = Bcrypt()


def create_app():

    app = Flask(__name__)

    # app config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config["MONGO_URI"] = os.getenv('DATABASE')
    app.config['MAIL_SERVER'] = os.getenv('SMTP_EMAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('SMTP_EMAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('SMTP_EMAIL')
    app.config['MAIL_PASSWORD'] = os.getenv('SMTP_EMAIL_PASSWORD')
    app.config['MAIL_USE_SSL'] = True

    # init app modules
    DB.init_app(app)
    MAIL.init_app(app)
    BCRYPT.init_app(app)

    # blueprints
    from .views import views
    app.register_blueprint(views)

    # error handler
    @app.errorhandler(404)
    def error404(e):
        return {"error": "404 error | page not found"}

    @app.errorhandler(405)
    def erro405(e):
        return {"error": "405 | request is not allowed"}

    return app
