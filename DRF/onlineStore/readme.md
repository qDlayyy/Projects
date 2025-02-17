# Online Store (DRF)

### Launching Instructions:
- Activate venv;
- Use "pip install -r requirements.txt" to install all nessessary packages, frameworks and etc.;
- Create migrations; 
- Migrate;
- Use "python manage.py generate_base" to create nessessary units;
- Use "celery -A store worker --loglevel=info" to allow celery work on the background;
- Use "celery -A store beat --loglevel=info" to allow celery work with periodical tasks on the background;
- Now it's ready to run.

### Celery:
- Registration confirmation email and order confirmation email are now sent via celery;
- Weekly email is sent to subscribers with the help of celery beat;
- The notification of the comming delivery is cent via celery only on working days not later than 8 p.m. 

### Tests:
The test.py file has 80 tests including:

- Models tests (Unit Tests)
- Serializers tests (Unit Tests)
- Views tests (Integration Tests)

Use "python manage.py test" to run them.

### Technical Task:
- 3 типа пользователей: клиент, незарегистрированный клиент, менеджер магазина;
- Данные клиента: имя, фамилия, эл. почта, телефон
- Менеджер магазина может просматривать, редактировать, добавлять и удалять товары в магазине
- Незарегистрированный клиент может просматривать товары в магазине
- Клиент может просматривать товары в магазине и добавлять их в свою
корзину
- Клиент может удалить товар из корзины
- Предусмотреть возможность добавлять скидки на определенные товары менеджером магазина
- Предусмотреть возможность у клиента подписаться на рассылку по эл. почте и получать уведомления об актуальных скидках один раз в неделю
- Предусмотреть возможность использования промокода для скидки на
итоговую сумму товаров в магазине. Добавить возможность для скидок
суммироваться и не суммироваться с промокодом
- Реализовать форму заказа с возможностью получить уведомление на
почту о доставке за день или за 6 часов или за 1 час

### Additional Task:
- Регистрация клиентов с подтверждением по электронной почте
- Добавить возможность добавления в корзину некоторого количества товара и редактирование этого количества в самой корзине
- Реализовать получение кэшбэка: после реализации заказа клиенту начисляется процент от суммы заказа, установленный менеджером магазина. Накопленный кэшбэк можно вычесть из суммы заказа, если сумма кэшбэка больше значения X, которое определяет менеджер магазина