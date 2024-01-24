#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        
        try:
            username = request.get_json()['username']
            password = request.get_json()['password']
            bio = request.get_json()['bio']
            image_url = request.get_json()['image_url']

            if not username or not password:
                return {'message': 'Invalid user data'}, 422

            user = User(
                username=username,
                bio=bio,
                image_url=image_url
            )

            user.password_hash = password

            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id

            return {
                'id': user.id,
                'username': user.username,
                'bio': user.bio,
                'image_url': user.image_url
            }, 201
        
        except IntegrityError:

            db.session.rollback()
            return {'message': 'Username already exists'}, 422


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'bio': user.bio,
                    'image_url': user.image_url
                }, 200
            else:
                return {'message': 'User not found'}, 404
            
        else:
            return {'message': 'Please Log in'}, 401

class Login(Resource):
    def post(self):

        username = request.get_json()['username']
        password = request.get_json()['password']

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'bio': user.bio,
                'image_url': user.image_url
            }, 201
        else:
            return {'message': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):

        session['user_id'] = None

        return {}, 204     

class RecipeIndex(Resource):

    def get(self):
        if session.get('user_id'):
            recipes = Recipe.query.filter(Recipe.user_id == session['user_id']).all()
            if recipes:
                return [{
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete
                } for recipe in recipes], 200
        else:
            return {'message': 'Please Log in'}, 401
    def post(self):
        
        if session.get('user_id'):
            title = request.get_json()['title']
            instructions = request.get_json()['instructions']
            minutes_to_complete = request.get_json()['minutes_to_complete']

            if not title or not instructions or not minutes_to_complete:
                return {'message': 'Invalid recipe data'}, 422

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete
            )

            recipe.user = User.query.filter(User.id == session['user_id']).first()
            
            user_dict = {
                'id': recipe.user.id,
                'username': recipe.user.username,
                'bio': recipe.user.bio,
                'image_url': recipe.user.image_url
            }

            if recipe.user:
                db.session.add(recipe)
                db.session.commit()

                return {
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': user_dict
                }, 201

            else:
                return {'message': 'Invalid user for recipe'}, 422
        
        else:
            return {'message': 'Please Log in'}, 401
            
        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)