from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional

db = SQLAlchemy()

class BaseMethods():
    def get_author_username(self) -> Optional[str]:
        if self.author:
            return self.author.username
        else:
            return None

    def get_proper_date(self) -> str:
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')


recipe_ingredients = db.Table('recipe_ingredients',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(162), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password=password)


    def check_password(self, password: str) -> bool:
        return check_password_hash(pwhash=self.password_hash, password=password)


    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }


class Ingredients(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)


    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name
        }

class Recipes(db.Model, BaseMethods):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    ingredients = db.relationship('Ingredients', secondary=recipe_ingredients, backref='recipes', lazy='dynamic')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('Users', backref='recipes')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'instructions': self.instructions,
            'ingredients': self.get_ingredients(),
            'author': self.get_author_username(),
            'created_at': self.get_proper_date()
        }


    def get_ingredients(self) -> list:
        return [ingredient.to_dict() for ingredient in self.ingredients]


class Comments(db.Model, BaseMethods):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipes', backref='comments')
    content = db.Column(db.String(256), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('Users', backref='comments')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    parent = db.relationship('Comments', remote_side=[id], backref='replies')


    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'recipe_id': self.recipe.id,
            'content': self.content,
            'author': self.get_author_username(),
            'created_at': self.get_proper_date(),
            'parent_id': self.parent.id if self.parent else None
        }
