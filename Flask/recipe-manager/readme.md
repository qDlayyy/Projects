# Recipe-manager(Flask API)

> Flask API Fast Practice

### Serialization
flask_marshmallow & marshmallow-sqlalchemy are used for serialization.

### Tests:
Pytest is used in the project. Fixtures are used to control data behavior both before and after tests run. Pytest gives the opportunity to parametrize tests, so it is also used in test cases.

- conftest.py module collects all the fixtures used in tests.
- test_api.py module has 28 tests.

Use "pytest" or "pytest -v" to run them.

### Technical Task:
- Возможность создания рецепта
- Отображение списка рецептов
- Отображение полной информации о рецепте
- Система комментариев для обмена мнениями о рецептах
- Возможность редактирования существующего рецепта
- Возможность удаления существующего рецепта
- Регистрация с аутентификацией
- Возможность ответа на существующий комментарий
