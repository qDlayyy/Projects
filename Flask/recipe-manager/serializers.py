from flask_marshmallow import Marshmallow
from models import Users, Ingredients, Recipes, Comments

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users


class IngredientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ingredients
        load_instance = True


class RecipesSchema(ma.SQLAlchemyAutoSchema):
    ingredients = ma.List(ma.Nested(IngredientSchema))

    class Meta:
        model = Recipes
        load_instance = True


class CommentsSchema(ma.SQLAlchemyAutoSchema):
    recipe_id = ma.Integer(attribute='recipe.id')
    parent_id = ma.Integer(attribute='parent.id', allow_none=True)

    class Meta:
        model = Comments
        load_instance = True


