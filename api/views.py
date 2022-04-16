from flask import Blueprint, request, make_response
from . import MAIL, DB, load_dotenv, BCRYPT
from flask_mail import Message
from datetime import datetime
from random import randint
import os


load_dotenv()

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return {'message': 'api for registration'}


# handle sing up method
@views.route('/singup', methods=['POST'])
def singup():
    if request.method == 'POST':
        data = request.get_json()
        if len(data['name']) < 3:
            return {"message": "name is too short"}, 400
        if len(data['email']) < 8 or '@' not in data['email']:
            return {'message': 'please enter a valid email'}, 400
        if len(data['phone_number']) < 5:
            return {'message': 'please enter your phone number'}, 400
        if len(data['password']) < 8:
            return {'message': 'please choose a long password'}, 400
        if data['password'] != data['conform_password']:
            return {'message': 'invalid password'}, 400
        # find duplicate user
        user = DB.db.users.find_one({"email": data['email']})
        if user:
            return {'message': 'user already exist'}, 400
        else:
            # hash password
            hashPassword = BCRYPT.generate_password_hash(data['password'])

            varifyCode = randint(1000, 9999)
            # insert user to the databse
            DB.db.users.insert_one({'name': data['name'], 'email': data['email'],
                                    'phone_number': data['phone_number'], 'password': hashPassword, 'verifyCode': varifyCode, 'isVerifyed': False, 'date': datetime.utcnow()})
            # verify user using mail
            msg = Message(sender=os.getenv('SMTP_EMAIL'), recipients=[
                data['email']], subject='Verify your email id', body=f" your verification code is {varifyCode}")
            MAIL.send(msg)

            return {'message': 'registration successfull'}, 200


# handle sing in method
@views.route('/singin', methods=['POST'])
def singin():
    if request.method == 'POST':
        if request.cookies.get('username'):
            return {'message': 'user already logged in'}, 200

        data = request.get_json()

        user = DB.db.users.find_one({'email': data['email']})
        if not user:
            return {'message': 'invalid user'}, 400
        if not BCRYPT.check_password_hash(user['password'], data['password']):
            return {'message': 'invalid user'}, 400

        res = make_response({'login': 'login successfull'})
        res.set_cookie('username', user['email'], max_age=60*60*24*30)
        return res


# handle logout
@views.route('/logout')
def logout():
    if request.cookies.get('username'):
        username = request.cookies.get('username')
        res = make_response({'message': 'user logout'})
        res.set_cookie('username', username, max_age=0)
        return res
    return {'message': 'user already logout'}, 200


# get user data
@views.route('/user_info', methods=['POST'])
def user_info():
    if request.method == 'POST':
        if not request.cookies.get('username'):
            return {'message': 'please login first'}, 00
        user = request.cookies.get('username')
        response = DB.db.users.find_one({'email': user})
        return {'email': response['email'], 'name': response['name'], 'phone_number': response['phone_number']}, 200


# verify email address
@views.route('/activate_account', methods=['POST'])
def activate_account():
    if request.method == 'POST':
        data = request.get_json()
        user = DB.db.users.find_one({'email': data['email']})
        if not user:
            return {'message': 'user not found'}, 400
        if user['verifyCode'] == data['verifyCode']:
            DB.db.users.update_one({'email': data['email']}, {"$set": {
                                   'isVerifyed': True}})
            return {'message': 'user has been verifyed'}, 200
        return {'message': 'server error'}, 400
