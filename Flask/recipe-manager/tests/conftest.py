import pytest
from app import create_app, db
from config import Config
from models import Users, Ingredients, Recipes, Comments

@pytest.fixture
def app():
    app = create_app(config_class=Config)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_data(client, init_database):
    author = Users(username='TestUser', email='test@gmail.com')
    author.set_password(password='testPass123')
    db.session.add(author)
    db.session.commit()

    simple_user = Users(username='TestUser2', email='test2@gmail.com')
    simple_user.set_password(password='testPass123')
    db.session.add(simple_user)
    db.session.commit()

    author_id = author.id
    recipe = Recipes(name="Pasta", instructions="Boil water", author_id=author_id)
    ingredient1 = Ingredients(name="Flour")
    ingredient2 = Ingredients(name="Water")
    
    db.session.add(recipe)
    db.session.add(ingredient1)
    db.session.add(ingredient2)
    db.session.commit()

    recipe.ingredients.append(ingredient1)
    recipe.ingredients.append(ingredient2)
    db.session.commit()

    simple_user_comment = Comments(recipe=recipe, author=simple_user, content='Test comment', parent=None)
    db.session.add(simple_user_comment)
    db.session.commit()

    return recipe
