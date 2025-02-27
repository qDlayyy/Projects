import bcrypt
from flask import Flask, request, jsonify, session, redirect, url_for
from datetime import timedelta
from functools import wraps
from psycopg2.errors import NotNullViolation

from config import Config
from key import APP_SECRET_KEY

from models import db, Users, Ingredients, Recipes, Comments
from serializers import ma, UserSchema, RecipesSchema, CommentsSchema
from service import get_author_obj


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)

    app.secret_key = APP_SECRET_KEY
    app.permanent_session_lifetime = timedelta(days=1)


    def login_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('user_id'):
                return func(*args, **kwargs)
            return redirect(url_for('login'))
        
        return wrapper


    @app.route('/api')
    def home():
        return jsonify({'detail': 'Home is ok.'}), 200


    @app.route('/registration', methods=['POST'])
    def registration():
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if Users.query.filter_by(username=username).first():
            return jsonify({'detail': 'User with this username exists.'}), 400
        
        try:
            new_user = Users(username=username, email=email)
            new_user.set_password(password=password)

            db.session.add(new_user)
            db.session.commit()

            user_schema = UserSchema()

            return user_schema.jsonify(new_user), 201


        except Exception as e:
            db.session.rollback()
            return jsonify({'detail': f'User cannot be created due to an occured error.',
                     'error': str(e)}), 500


    @app.route('/login', methods=['POST'])
    def login():
        data = request.json

        username = data.get('username')
        password = data.get('password')
        user = Users.query.filter_by(username=username).first()
        
        try:
            if user and user.check_password(password=password):
                session['user_id'] = user.id
                return jsonify({'detail': 'Successfully logged in.'}), 200

            return jsonify({'detail': 'Unable to log in due to wrong data. No such user or incorrect password.'}), 401

        except Exception as e:
            return jsonify({'detail': f'You cannot be logged in due to an occured error.',
                     'error': str(e)}), 500


    @app.route('/logout', methods=['GET'])
    def logout():
        session.pop('user_id', None)

        return jsonify({'detail': 'Successfully logged out.'}), 200
            

    @app.route('/api/recipes', methods=['GET'])
    def get_recipes():
        recipes = Recipes.query.all()

        for recipe in recipes:
            print(f'\n\n {recipe.__dict__}\n\n')

        recipe_schema = RecipesSchema(many=True)
        
        return recipe_schema.jsonify(recipes), 200

    
    @app.route('/api/recipes', methods=['POST'])
    @login_decorator
    def create_recipe():
        data = request.get_json()

        name = data.get('name')
        instructions = data.get('instructions')
        ingredients = data.get('ingredients')
        author = get_author_obj(author_id=session.get('user_id'))

        print(name, instructions, ingredients, author)

        try:
            if not name or not instructions or (ingredients is not None and len(ingredients) == 0):
                raise Exception("Invalid data provided.")
            
            recipe = Recipes(name=name, instructions=instructions, author=author)
            
            for ingredient in ingredients:
                existing_ingredient = Ingredients.query.filter_by(name=ingredient).first()

                if existing_ingredient:
                    recipe.ingredients.append(existing_ingredient)
                
                else:
                    new_ingredient = Ingredients(name=ingredient)
                    db.session.add(new_ingredient)
                    recipe.ingredients.append(new_ingredient)
                print(f'\n{recipe.__dict__}\n')
            
            db.session.add(recipe)
            db.session.commit()

            print('ff')

            recipe_schema = RecipesSchema()

            return recipe_schema.jsonify(recipe), 201

        except Exception as e:
            print(f'\n\n{e}\n\n')
            db.session.rollback()
            return jsonify({'detail': f'No recipes have been added due to the occured error.',
                     'error': f'{e}.'}), 400


    @app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
    def get_recipe(recipe_id):
        recipe = Recipes.query.filter_by(id=recipe_id).first()

        if recipe is None:
            return jsonify({'detail': 'Recipe not found.'}), 404

        recipe_schema = RecipesSchema()

        return recipe_schema.jsonify(recipe), 200


    @app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
    @login_decorator
    def update_recipe(recipe_id):
        recipe = Recipes.query.filter_by(id=recipe_id).first()

        if recipe is None:
            return jsonify({'detail': 'Recipe not found.'}), 404
        
        if recipe.author.id == session.get('user_id'):
            data = request.get_json()
            new_name = data.get('name', recipe.name)
            new_instructions = data.get('instructions', recipe.instructions)
            new_ingredients = data.get('ingredients', None)

            if new_ingredients:
                current_ingredients = {ingredient.name for ingredient in recipe.ingredients}
                ingredients_to_add = {ingredient_name for ingredient_name in new_ingredients if ingredient_name not in current_ingredients}
                ingredients_to_remove = {ingredient_name for ingredient_name in current_ingredients if ingredient_name not in new_ingredients}
                
            try:
                if new_ingredients:
                    for ingredient in ingredients_to_add:
                        found_ingredient = Ingredients.query.filter_by(name=ingredient).first()
                        
                        if found_ingredient:
                            recipe.ingredients.append(found_ingredient)
                        
                        else:
                            new_ingredient = Ingredients(name=ingredient)
                            db.session.add(new_ingredient)
                            recipe.ingredients.append(new_ingredient)
                    
                    for ingredient in ingredients_to_remove:
                        found_ingredient = Ingredients.query.filter_by(name=ingredient).first()
                        recipe.ingredients.remove(found_ingredient)
                
                recipe.name = new_name
                recipe.instructions = new_instructions

                db.session.commit()
                return jsonify({'detail': 'Recipe updated successfully.'}), 200
            
            except Exception as e:
                db.session.rollback()
                return jsonify({'detail': f'No changes have been done due to the occured error. {e}.'}), 400
        
        else:
            return jsonify({'detail': f'You cannot change this recipe.'}), 403


    @app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
    @login_decorator
    def delete_recipe(recipe_id):
        recipe = Recipes.query.filter_by(id=recipe_id).first()

        if recipe is None:
            return jsonify({'detail': 'Recipe not found.'}), 404
        
        if recipe.author.id == session.get('user_id'):
            comments = Comments.query.filter_by(recipe=recipe).all()

            try:
                if comments:
                    for comment in comments:
                        db.session.delete(comment)
                db.session.delete(recipe)
                db.session.commit()
                return jsonify({'detail': 'The recipe has been successfully deleted.'}), 203
            
            except Exception as e:
                app.logger.error(f"Error deleting recipe: {e}")
                db.session.rollback()
                return jsonify({'detail': f'No recipes have been deleted due to the occured error.',
                                'error': f'{e}.'}), 400

        else:
            return jsonify({'detail': f'You cannot delete this recipe.'}), 403

    
    @app.route('/api/recipes/<int:recipe_id>/comments', methods=['POST'])
    @login_decorator
    def create_comment(recipe_id):
        data = request.get_json()

        content = data.get('content')
        author = get_author_obj(session.get('user_id'))
        reply_id = data.get('reply_id')

        recipe = Recipes.query.filter_by(id=recipe_id).first()
        if recipe is None:
            return jsonify({'detail': 'Recipe not found.'}), 404
        
        parent_comment = Comments.query.filter_by(id=reply_id).first()

        try:
            new_comment = Comments(recipe=recipe, author=author, content=content, parent=parent_comment)

            db.session.add(new_comment)
            db.session.commit()

            comments_schema = CommentsSchema()
            return comments_schema.jsonify(new_comment), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'detail': f'No comments have been created due to the occured error.',
                            'error': f'{e}.'}), 400


    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
