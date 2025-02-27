import pytest
import json
from models import Users, Recipes


def test_home(client):
    """
    Test to make sure that test set up is correct
    """
    response = client.get('/api')
    assert response.status_code == 200
    assert response.get_json() == {'detail': 'Home is ok.'} 


@pytest.mark.parametrize("username, email, password, expected_status, expected_detail", [
    ('testuser', 'testuser@example.com', 'password123', 201, None),
    ('existinguser', 'exis@example.com', 'password123', 400, 'User with this username exists.'),
    (None, 'testuser@example.com', 'password123', 500, 'User cannot be created due to an occured error.')])
def test_registration(client, init_database, username, email, password, expected_status, expected_detail):
    """
    Fully new user registration and a try to register as a registered user
    """

    if username == 'existinguser':
        client.post('/registration', json={
            'username': 'existinguser',
            'email': 'exis@example.com',
            'password': 'password123'
        })
    
    response = client.post('/registration', json={
        'username': username,
        'email': email,
        'password': password
    })

    assert response.status_code == expected_status
    if expected_detail:
        assert response.get_json()['detail'] == expected_detail
        
    else:
        assert 'username' in response.get_json()
        assert response.json['username'] == username
        assert Users.query.filter_by(username=username).first() is not None


@pytest.mark.parametrize("username, password, expected_status, expected_detail",[
    ('testusername', 'test123123', 200, 'Successfully logged in.'),
    ('testusername', 'wrongPass', 401, 'Unable to log in due to wrong data. No such user or incorrect password.'),
    ('nonRegister', '123123', 401,  'Unable to log in due to wrong data. No such user or incorrect password.'),
    ('testusername', None, 500, 'You cannot be logged in due to an occured error.')
])
def test_login(client, init_database, username, password, expected_status, expected_detail):
    """
    Test for log in. 
    Successfull log in, incorrect credentials, non-registered data, missing data. 
    """

    if username == 'testusername':
        client.post('/registration', json={
            'username': 'testusername',
            'email': 'exis@example.com',
            'password': 'test123123'
        })

    response = client.post('/login', json={
        'username': username,
        'password': password
    })
    
    assert response.status_code == expected_status
    assert response.json['detail'] == expected_detail
    

@pytest.mark.parametrize("is_user_in_session, expected_status, expected_json", [
    (True, 200, {'detail': 'Successfully logged out.'}),
    (False, 200, {'detail': 'Successfully logged out.'})])
def test_logout(client, init_database, is_user_in_session, expected_status, expected_json):
    """
    Log out test.
    Logged in user and not logged in user.
    """

    if is_user_in_session:
        with client.session_transaction() as session:
            session['user_id'] = 1
    
    response = client.get('/logout')

    assert response.status_code == expected_status
    assert response.json == expected_json

    with client.session_transaction() as session:
        if is_user_in_session:
            assert 'user_id' not in session
        else:
            assert 'user_id' not in session


@pytest.mark.parametrize("expected_name, expected_ingrediets_num, expected_status", [
    ("Pasta", 2, 200)
])
def get_all_recipes(client, sample_data, expected_name, expected_ingrediets_num, expected_status):
    response = client.get('/api/recipes')

    assert response.status_code == expected_status

    json_response = response.get_json()
    assert json_response.get('name') == expected_name
    assert len(json_response['ingredients']) == expected_ingrediets_num


@pytest.mark.parametrize("payload, expected_status, expected_response", [
    ({"name": "No auth", "instructions": "Boil water", "ingredients": ["Pasta", "Salt"]}, 302, None),
    ({"name": "Pasta", "instructions": "Boil water", "ingredients": ["Pasta", "Salt"]}, 201, "Pasta"),
    ({"name": "Salad", "instructions": "Mix ingredients", "ingredients": ["Lettuce", "Tomato"]}, 201, "Salad"),
    ({"name": "Pizza", "instructions": "Bake", "ingredients": []}, 400, 'No recipes have been added due to the occured error.'),
    ({"name": "", "instructions": "Bake", "ingredients": ["Dough"]}, 400, 'No recipes have been added due to the occured error.')
])
def test_create_recipe(client, init_database, payload, expected_status, expected_response):
    """
    New recipe creation test.
    Non-authorized try(redirect), successfull try, successfull try, bad credentials, bad credentials.
    """
    if payload['name'] != 'No auth':
        with client.session_transaction() as session:
            session['user_id'] = 1
    
    response = client.post('/api/recipes', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == expected_status
    response_json = response.json
    if response.status_code == 201:
        assert response_json['name'] == expected_response
    
    elif response.status_code == 302:
        assert response_json is None
    
    else:
        assert expected_response in response_json['detail']


@pytest.mark.parametrize("test_id, expected_data, expected_status", [
    (1, {"name": "Pasta", "instructions": "Boil water", "ingredients": ["Flour", "Water"], "comments": 'Test comment'}, 200),
    (2, None, 404)])
def test_get_retrive_recipe(client, sample_data, test_id, expected_data, expected_status):
    """
    Get retrive recipe test.
    Successfull, Incorrect recipe id.
    """
    
    if test_id == 1:
        response = client.get(f'/api/recipes/{sample_data.id}')
        json_response = response.get_json()
        json_response.get('name') == expected_data.get('name')
        json_response.get('instructions') == expected_data.get('instructions')
        len(json_response.get('ingredients')) == 2
        json_response.get('comments') == expected_data.get('comments')

    else:
        response = client.get(f'/api/recipes/500')
    
    assert response.status_code == expected_status


@pytest.mark.parametrize("user_id, payload, expected_status, expected_detail", [
    (1, {"name": "New Pasta", "instructions": "New instruction", "ingredients": ["Flour", "Water"]}, 200, "Recipe updated successfully."),
    (1, {"name": "New Pasta"}, 200, "Recipe updated successfully."),
    (2, {"name": "Attempted Change"}, 403, "You cannot change this recipe."),
    (1, {"ingredients": ["New Ingredient"]}, 200, "Recipe updated successfully."),
    (1, {"name": "Nonexistent Recipe", "ingredients": ["Nonexistent Ingredient"]}, 200, "Recipe updated successfully.")
])
def test_recipe_update(client, sample_data, user_id, payload, expected_status, expected_detail):
    """
    Update retrive recipe test.
    Successfull(full data provided), Successfull(partial data provided), 403(Incorrect user_id), Successfull(partial data provided), Successfull(partial data provided & non-existing ingredient).
    """
    
    with client.session_transaction() as session:
        session['user_id'] = user_id
    
    response = client.put(f'/api/recipes/{sample_data.id}', json=payload)
    assert response.status_code == expected_status

    json_data = response.get_json()
    assert json_data['detail'] == expected_detail

    if expected_status == 200:
        updated_recipe = Recipes.query.filter_by(id=sample_data.id).first()
        assert updated_recipe.name == payload.get("name", sample_data.name)
        updated_ingredients = {ingredient.name for ingredient in updated_recipe.ingredients}

        if "ingredients" in payload:
            assert all(ingredient in updated_ingredients for ingredient in payload["ingredients"])


@pytest.mark.parametrize("user_id, expected_status, expected_detail", [
    (1, 203, 'The recipe has been successfully deleted.'),
    (2, 403, 'You cannot delete this recipe.')
])
def test_recipe_delete(client, sample_data, user_id, expected_status, expected_detail):

    with client.session_transaction() as session:
        session['user_id'] = user_id
    
    response = client.delete(f'/api/recipes/{sample_data.id}')

    assert response.status_code == expected_status
    
    json_response = response.get_json()
    assert json_response.get('detail') == expected_detail


@pytest.mark.parametrize("author_id, content, reply_id, expected_status", [
    (2, "Great recipe!", None, 201),
    (2, "Reply to the pre-created comment in simple data", 1, 201),
    (2, "Reply to the pre-created comment in simple data", 999, 201),
    (None, "Nice!", None, 302),
])
def test_create_comment(client, sample_data, author_id, content, reply_id, expected_status):
    """
    Comments creation test.
    Successfull(no reply), Successfull(with reply), Successfull(with incorrect reply - the comment is created with no reply), Anathorized try.
    """
    if author_id is not None:
        with client.session_transaction() as session:
            session['user_id'] = author_id

    response = client.post(f'/api/recipes/{sample_data.id}/comments', json={
        'content': content,
        'reply_id': reply_id,
    })

    assert response.status_code == expected_status

    if expected_status == 201:
        comment_data = response.get_json()
        assert comment_data['content'] == content