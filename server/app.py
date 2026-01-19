#!/usr/bin/env python3

from flask import Flask, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)

# --- CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'
app.json.compact = False

# --- INIT ---
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# --------------------
# SESSION UTILITIES
# --------------------

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

# --------------------
# ARTICLES
# --------------------

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = session.get('page_views', 0) + 1

        if session['page_views'] <= 3:
            article = Article.query.filter_by(id=id).first()
            return article.to_dict(), 200

        return {'message': 'Maximum pageview limit reached'}, 401

# --------------------
# AUTHENTICATION
# --------------------

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()

        session['user_id'] = user.id
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if not user_id:
            return {}, 401

        user = User.query.get(user_id)
        return user.to_dict(), 200

# --------------------
# ROUTES
# --------------------

api.add_resource(ClearSession, '/clear')

api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

# --------------------

if __name__ == '__main__':
    app.run(port=5555, debug=True)
