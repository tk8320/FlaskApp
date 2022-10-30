from application import api
from flask import request, make_response, jsonify
from flask_restful import Resource, abort
from application.models import db, User, News
from sqlalchemy.exc import IntegrityError
import hashlib
from application.routes import crypt, db_id
from application.models import secret_key
from application.routes import n

master_key = '2f58d9d528bb47fc6f116e257b7470a265f4b8c7c72b9c09491ea654e991265351c89de87b476f457c3cf356a4346893e8d309960677e0088a14e7e3c4fdb449'


class addUser(Resource):
    def post(self):
        json_data = request.json
        # hash_pass = hashlib.sha512(json_data['password'].encode()).hexdigest()
        hash_pass = crypt(json_data['username'], json_data['password'])
        if 'contact_no' in json_data:
            s = User(json_data['username'], hash_pass, json_data['contact_no'])
        else:
            s = User(json_data['username'], hash_pass)
        db.session.add(s)
        # db_id += 1
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify({"message": "Username already exist"})

        return make_response(
            jsonify({"username": json_data['username'], "password": hash_pass, "message": "user created successfully"}),
            200)


class deleteUser(Resource):
    def delete(self):
        json_data = request.json

        x = User.query.filter_by(username=json_data['username']).first()
        if x is None:
            abort(400, message="USER NOT EXIST")
            # return make_response(jsonify({"message": "USER NOT FOUND"}), 404)

        if crypt(json_data['username'], json_data['password'], x.id) == x.password or hashlib.sha512(
                json_data['master_key'].encode()).hexdigest() == master_key:
            db.session.delete(x)
            db.session.commit()
            return make_response(jsonify({"message": "DELETED SUCCESSFULLY"}), 200)
        else:
            return make_response(jsonify({"message": "WRONG PASSWORD"}), 400)


class addNews(Resource):
    def post(self):
        json_data = request.json
        if 'heading' not in json_data:
            return jsonify({"message": "Heading is required"})
        else:
            x = News(json_data['heading'], json_data['description'])
            db.session.add(x)
            try:
                db.session.commit()
            except IntegrityError:
                return jsonify({"message": "Heading Already Exists"})
            return jsonify({"message": "News created successfully"})


class ChangePassword(Resource):
    def post(self):
        json_data = request.json
        if 'username' not in json_data or 'password' not in json_data or 'confirm_password' not in json_data or 'current_password' not in json_data:
            return make_response(jsonify({"error": "mandatory fields are not preset"}), 400)
        else:
            x = User.query.filter_by(username=json_data['username']).first()
            if x is None:
                return make_response(jsonify({"error": "No User Exist"}), 400)
            else:
                if x.password == crypt(json_data['username'], json_data['current_password'], x.id) and json_data[
                    'password'] == json_data['confirm_password']:
                    x.password = crypt(json_data['username'], json_data['password'], x.id)
                    db.session.commit()
                    return make_response(jsonify({"message": "Password Changed Successfully"}), 200)
                else:
                    return make_response(jsonify({"error": "wrong password or password Didn't matched"}), 400)


class unlockAccount(Resource):
    def post(self):
        json_data = request.json
        if 'username' not in json_data or 'master_key' not in json_data:
            return make_response(jsonify({"error": "Insufficient data"}, 400))
        else:
            if hashlib.sha512(json_data['master_key'].encode()).hexdigest() == master_key:
                x = User.query.filter_by(username=json_data['username']).first()
                if x is None:
                    return make_response(jsonify({"error": "User Not found"}))
                elif x.count < n:
                    return make_response(jsonify({"error": "Account is not locked"}))
                else:
                    x.count = 0
                    try:
                        db.session.commit()
                    except:
                        return make_response(jsonify({"error": "Something went wrong"}))
                    return make_response(jsonify({"message": "Account Successfully Unlocked"}))
            else:
                return make_response(jsonify({"error": "Wrong masterkey"}))


api.add_resource(addUser, "/api")
api.add_resource(deleteUser, "/api")
api.add_resource(addNews, "/api/add_news")
api.add_resource(ChangePassword, "/api/change-password")
api.add_resource(unlockAccount, "/api/unlock")
