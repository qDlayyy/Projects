from rest_framework import status
from django.test import TestCase, RequestFactory
from http.client import responses
from .models import StoreBase, User, Profile, Products, CartItem, OrderedItems, Order, Promocodes
from .serializers import StoreBaseSerializer, UserSerializer, ProfileSerializer, ProductsSerializer, CartItemSerializer, UserRegisterSerializer, OrderedItemsSerializer, OrderConfirmationSerilizer, PromocodeSerializer
from .views import AdminStoreBaseView
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError
# from rest_framework.reverse import reverse
from django.urls import reverse
from decimal import Decimal

# Models Tests
class BaseModelTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.store = StoreBase.objects.create(
            name = 'Admin',
            cashback_access_from = 300,
            cashback_percentage = 3
        )
        self.request_factory = RequestFactory()

        self.user = User.objects.create_user(
            username='TestUsername', 
            first_name='TestName', 
            last_name='TestSurname',
            email='test@gmail.com',
            password='testpass1'
            )
        
        self.admin = User.objects.create_superuser(
            username='test_admin', 
            password='testpass1'
            )

        self.profile = Profile.objects.create(
            user = self.user,
            phone = '+375297878787',
            is_subscribed = False,
            cashback = 0,
            token = None
        )
        
        self.apple = Products.objects.create(
            name = 'Apple',
            description = 'Some desc',
            price = 140.20,
            discount_percentage = 3
        )

        self.pear = Products.objects.create(
            name = 'Pear',
            description = 'Some other desc',
            price = 90.32,
            discount_percentage = 5
        )

        self.cart_item = CartItem.objects.create(
            user = self.user,
            item = self.apple,
            quantity = 5
        )

        self.ordered_apples = OrderedItems.objects.create(
            user = self.user,
            item = self.apple,
            quantity = 3
        )

        self.ordered_pears = OrderedItems.objects.create(
            user = self.user,
            item = self.pear,
            quantity = 5
        )

        self.order_one = Order.objects.create(
            user = self.user,
            email = self.user.email,
            address = '1 Y Street',
            notification_time = '1h',
            price = 120
        )

        self.order_one.orders.add(self.ordered_apples, self.ordered_pears)

        self.promocode = Promocodes.objects.create(
            code = 'l0DeUi',
            sale_percentage = 3,
            is_active = True,
            summarizes_with_other_sales = False
        )


class ModelProfileTestCases(BaseModelTestCase):

    def test_profile_native_creation_1(self):

        test_data = {'user': self.user, 'phone': '+375297878787', 'is_subscribed': False, 'cashback': 0, 'token': None}

        profile = Profile.objects.create(
            user = test_data['user'],
            phone = test_data['phone'],
            is_subscribed = test_data['is_subscribed'],
            cashback = test_data['cashback'],
            token = test_data['token']
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone, '+375297878787')
        self.assertEqual(profile.is_subscribed, False)
        self.assertEqual(profile.cashback, 0)
        self.assertEqual(profile.token, None)
    
    
    def test_profile_native_creation_2(self):

        test_data = {'user': self.user, 'phone': '+375297878787'}


        profile = Profile.objects.create(
            user = test_data['user'],
            phone = test_data['phone'],
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone, '+375297878787')
        self.assertEqual(profile.is_subscribed, False)
        self.assertEqual(profile.cashback, 0)
        self.assertEqual(profile.token, None)


class ModelStoreBaseTestCases(TestCase):
    
    def setUp(self):
        return super().setUp()


    def test_store_base_creation_default(self):
        
        store_base = StoreBase.objects.create()

        self.assertEqual(store_base.name, 'Admin')
        self.assertEqual(store_base.cashback_access_from, 300)
        self.assertEqual(store_base.cashback_percentage, 3)

    
    def test_store_base_creation_native(self):
        
        test_data = {
            'name': 'TestName',
            'cashback_access_from': 450,
            'cashback_percentage': 5
        }

        store_base = StoreBase.objects.create(
            name = test_data['name'],
            cashback_access_from = test_data['cashback_access_from'],
            cashback_percentage = test_data['cashback_percentage']
        )

        self.assertEqual(store_base.name, 'TestName')
        self.assertEqual(store_base.cashback_access_from, 450)
        self.assertEqual(store_base.cashback_percentage, 5)

    
    def test_store_base_creation_wrong(self):
        
        test_data = {
            'name': 'TestName',
            'cashback_access_from': -500,
            'cashback_percentage': 5
        }

        with self.assertRaises(ValidationError):
            store = StoreBase.objects.create(
                name = test_data['name'],
                cashback_access_from = test_data['cashback_access_from'],
                cashback_percentage = test_data['cashback_percentage']
            )
            store.full_clean()
        

class ModelProductsTestCases(TestCase):
   
    def setUp(self):
        return super().setUp()
    
    def test_products_creation_native(self):

        test_data = {
            'name': 'Apple',
            'description': 'Some disc for apple',
            'price': 20,
            'discount_percentage': 3
        }

        apple = Products.objects.create(
            name = test_data['name'],
            description = test_data['description'],
            price = test_data['price'],
            discount_percentage = test_data['discount_percentage']
        )

        self.assertEqual(apple.name, 'Apple')
        self.assertEqual(apple.description, 'Some disc for apple')
        self.assertEqual(apple.price, 20)
        self.assertEqual(apple.discount_percentage, 3)
    

    def test_products_creation_default(self):

        test_data = {
            'name': 'Apple',
            'description': 'Some disc for apple',
            'price': 20,
        }

        apple = Products.objects.create(
            name = test_data['name'],
            description = test_data['description'],
            price = test_data['price'],
        )

        self.assertEqual(apple.name, 'Apple')
        self.assertEqual(apple.description, 'Some disc for apple')
        self.assertEqual(apple.price, 20)
        self.assertEqual(apple.discount_percentage, 0)
    

    def test_products_creation_wrong(self):

        test_data = {
            'name': 'AppleAndWayMoreThan20Symbols',
            'description': 'Some disc for apple',
            'price': 20,
        }

        with self.assertRaises(ValidationError):
            apple = Products.objects.create(
                name = test_data['name'],
                description = test_data['description'],
                price = test_data['price'],
            )

            apple.full_clean()


    def test_get_final_price_method(self):
        test_data = {
            'name': 'Apple',
            'description': 'Some disc for apple',
            'price': 20,
            'discount_percentage': 3
        }

        apple = Products.objects.create(
            name = test_data['name'],
            description = test_data['description'],
            price = test_data['price'],
            discount_percentage = test_data['discount_percentage']
        )

        final_price = float(apple.get_final_price())

        self.assertEqual(final_price, 19.4)
            



        # self.assertEqual(store_base.name, test_data['name'])
        # self.assertEqual(store_base.cashback_access_from, test_data['cashback_access_from'])
        # self.assertEqual(store_base.cashback_percentage, test_data['cashback_percentage'])
    

        # self.cart_item_one = CartItem.objects.create(
        #     user = self.user,
        #     item = self.product_one,
        #     quantity = 4
        # )

        # self.cart_item_one = CartItem.objects.create(
        #     user = self.user,
        #     item = self.product_two,
        #     quantity = 5
        # )


        # self.order_item_one = OrderedItems.objects.create(
        #     user = self.user,
        #     item = self.product_one,
        #     quantity = 4
        # )

        # self.order_item_two = OrderedItems.objects.create(
        #     user = self.user,
        #     item = self.product_two,
        #     quantity = 5
        # )


class ModelCartItemTestCases(BaseModelTestCase):

    def test_cart_item_creation_native(self):

        test_data = {
            'user': self.user,
            'item': self.apple,
            'quantity': 3
        }

        cart_item = CartItem.objects.create(
            user = test_data['user'],
            item = test_data['item'],
            quantity = test_data['quantity']
        )

        self.assertEqual(cart_item.user.username, 'TestUsername')
        self.assertEqual(cart_item.item.name, 'Apple')
        self.assertEqual(cart_item.quantity, 3)


    def test_cart_item_creation_default(self):

        test_data = {
            'user': self.user,
            'item': self.pear,
        }

        cart_item = CartItem.objects.create(
            user = test_data['user'],
            item = test_data['item'],
        )

        self.assertEqual(cart_item.user.username, 'TestUsername')
        self.assertEqual(cart_item.item.name, 'Pear')
        self.assertEqual(cart_item.quantity, 1)


class ModelOrderedItemsTestCases(BaseModelTestCase):
    
    def test_ordered_item_creation_native(self):

        test_data = {
            'user': self.user,
            'item': self.apple,
            'quantity': 3
        }

        ordered_item = OrderedItems.objects.create(
            user = test_data['user'],
            item = test_data['item'],
            quantity = test_data['quantity']
        )

        self.assertEqual(ordered_item.user.username, 'TestUsername')
        self.assertEqual(ordered_item.item.name, 'Apple')
        self.assertEqual(ordered_item.quantity, 3)


    def test_ordered_item_creation_default(self):

        test_data = {
            'user': self.user,
            'item': self.pear,
        }

        ordered_item = OrderedItems.objects.create(
            user = test_data['user'],
            item = test_data['item'],
        )

        self.assertEqual(ordered_item.user.username, 'TestUsername')
        self.assertEqual(ordered_item.item.name, 'Pear')
        self.assertEqual(ordered_item.quantity, 1)


class ModelOrderTestCases(BaseModelTestCase):

    def test_order_creation_native(self):
        
        test_data = {
            'user': self.user,
            'email': 'test@gmail.com',
            'address': 'Testing address',
            'notification_time': '1h',
            'price': 120
        }

        order = Order.objects.create(
            user = test_data['user'],
            email = test_data['email'],
            address = test_data['address'],
            notification_time = test_data['notification_time'],
            price = test_data['price']
        )

        order.orders.add(self.ordered_apples, self.ordered_pears)
        

        self.assertEqual(order.user.username, 'TestUsername')
        self.assertEqual(order.email, 'test@gmail.com')
        self.assertEqual(order.address, 'Testing address')
        self.assertEqual(order.notification_time, '1h')
        self.assertEqual(order.price, 120.00)
        self.assertEqual(order.orders.count(), 2)

    
    def test_order_creation_default(self):
        
        test_data = {
            'user': self.user,
            'email': 'test@gmail.com',
            'address': 'Testing address',
            'price': 120
        }

        order = Order.objects.create(
            user = test_data['user'],
            email = test_data['email'],
            address = test_data['address'],
            price = test_data['price']
        )

        order.orders.add(self.ordered_apples, self.ordered_pears)
        

        self.assertEqual(order.user.username, 'TestUsername')
        self.assertEqual(order.email, 'test@gmail.com')
        self.assertEqual(order.address, 'Testing address')
        self.assertEqual(order.notification_time, '1h')
        self.assertEqual(order.price, 120.00)
        self.assertEqual(order.orders.count(), 2)
    

    def test_order_creation_wrong(self):
        
        test_data = {
            'user': self.user,
            'email': 'test@gmail.com',
            'address': 'Testing address',
            'notification_time': '3h',
            'price': 120
        }

        with self.assertRaises(ValidationError):
            order = Order.objects.create(
                user = test_data['user'],
                email = test_data['email'],
                address = test_data['address'],
                notification_time = test_data['notification_time'],
                price = test_data['price']
            )

            order.orders.add(self.ordered_apples, self.ordered_pears)

            order.full_clean()


class ModelPromocodesTestCase(TestCase):
    
    def setUp(self):
        return super().setUp()
    

    def test_promocode_creation_native(self):

        test_data = {
            'code': '02TrDK',
            'sale_percentage': 5,
            'is_active': False,
            'summarizes_with_other_sales': False
        }

        promocode = Promocodes.objects.create(
            code = test_data['code'],
            sale_percentage = test_data['sale_percentage'],
            is_active = test_data['is_active'],
            summarizes_with_other_sales = test_data['summarizes_with_other_sales']
        )

        self.assertEqual(promocode.code, '02TrDK')
        self.assertEqual(promocode.sale_percentage, 5)
        self.assertEqual(promocode.is_active, False)
        self.assertEqual(promocode.summarizes_with_other_sales, False)


    def test_promocode_creation_default(self):

        test_data = {
            'code': '02TrDK',
            'sale_percentage': 5
        }

        promocode = Promocodes.objects.create(
            code = test_data['code'],
            sale_percentage = test_data['sale_percentage']
        )

        self.assertEqual(promocode.code, '02TrDK')
        self.assertEqual(promocode.sale_percentage, 5)
        self.assertEqual(promocode.is_active, False)
        self.assertEqual(promocode.summarizes_with_other_sales, False)


# Serializers Tests
class StoreBaseSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        serializer = StoreBaseSerializer(instance=self.store)
        data = serializer.data

        self.assertEqual(data['id'], self.store.id)
        self.assertEqual(data['name'], 'Admin')
        self.assertEqual(Decimal(data['cashback_access_from']), Decimal(300))
        self.assertEqual(data['cashback_percentage'], 3)
        self.assertIn('update_url', data)

    
    def test_invalid_serialization(self):

        test_data = {
            'name': '',
            'cashback_access_from': -20,
            'cashback_percentage': 120
        }   

        serializer = StoreBaseSerializer(data=test_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('cashback_access_from', serializer.errors)
        self.assertIn('cashback_percentage', serializer.errors)
    

    def test_get_update_url(self):
        request = self.request_factory.get(reverse('admin-detail-store-settings', kwargs={'pk': self.store.id}))
        serializer = StoreBaseSerializer(instance=self.store, context={'request': request})
        update_url = serializer.data['update_url']
        expected_url = f'http://testserver/api/admin/settings/{self.store.pk}'
        self.assertEqual(update_url, expected_url)


class UserSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        instance = self.user
        serializer = UserSerializer(instance=instance)
        data = serializer.data

        self.assertEqual(data['id'], self.user.pk)
        self.assertEqual(data['username'], 'TestUsername')
        self.assertEqual(data['first_name'], 'TestName')
        self.assertEqual(data['last_name'], 'TestSurname')
        self.assertEqual(data['email'], 'test@gmail.com')
    

class ProfileSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        instance = self.profile
        serializer = ProfileSerializer(instance=instance)
        data = serializer.data

        user_info_expected_data = {
            'id': 1,
            'username': 'TestUsername',
            'first_name': 'TestName',
            'last_name': 'TestSurname',
            'email': 'test@gmail.com'
        }

        self.assertEqual(data['user_info'], user_info_expected_data)
        self.assertEqual(data['user_phone'], '+375297878787')
        self.assertEqual(Decimal(data['user_cashback']), Decimal(0))
        self.assertEqual(data['is_subscribed'], False)


class ProductSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        instance = self.apple
        serializer = ProductsSerializer(instance=instance)
        data = serializer.data

        self.assertEqual(data['id'], self.apple.id)
        self.assertEqual(data['name'], 'Apple')
        self.assertEqual(data['description'], 'Some desc')
        self.assertEqual(float(data['price']), float(140.20))
        self.assertEqual(data['discount_percentage'], 3)
        self.assertIn('detail_product_url', data)
        self.assertIn('final_price', data)
    

    def test_get_final_price(self):
        instance = self.apple
        serializer = ProductsSerializer(instance=instance)
        data = serializer.data

        self.assertEqual(data['final_price'], 135.99)
    

    def test_get_detail_product_url(self):
        instance = self.apple
        request = self.request_factory.get(reverse('detail-product', kwargs={'pk': instance.pk}))
        serializer = ProductsSerializer(instance=instance, context={'request': request})
        data = serializer.data
        detail_product_url = data['detail_product_url']
        expected_url = f'http://testserver/api/products/{instance.pk}/'

        self.assertEqual(detail_product_url, expected_url)


class CartItemSerializerTestCase(BaseModelTestCase):
    
    def test_valid_serialization(self):
        instance = self.cart_item
        serializer = CartItemSerializer(instance=instance)
        data = serializer.data

        self.assertEqual(data['id'], 1)
        self.assertEqual(data['item'], instance.item.pk)
        self.assertEqual(data['quantity'], 5)


class UserRegistrationSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        test_data = {
            'username': 'test_user',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'email': 'a@gmail.com',
            'password': '12345678Test',
            'phone': '+375297878787'
        }

        serializer = UserRegisterSerializer(data=test_data)
        
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(User.objects.count(), 3) # 2 User objects has already been created in base setUp.
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.first_name, 'test_name')
        self.assertEqual(user.last_name, 'test_last_name')
        self.assertEqual(user.email, 'a@gmail.com')
        self.assertTrue(user.check_password('12345678Test'))

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.phone, '+375297878787')
        self.assertEqual(profile.token, None)
    

    def test_invalid_serialization(self):
        test_data = {
            'username': 'test_user',
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'email': 'not_a_valid_email',
            'password': '12345678Test',
            'phone': '+375297878787'
        }

        serializer = UserRegisterSerializer(data=test_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class OrderedItemsSerializerTestCase(BaseModelTestCase):
    
    def test_valid_serialization(self):
        instance = self.ordered_apples
        serializer = OrderedItemsSerializer(instance=instance)
        data = serializer.data

        self.assertEqual(data['item'], 1)
        self.assertEqual(data['quantity'], 3)


class OrderConfirmationSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        instance = self.order_one
        serializer = OrderConfirmationSerilizer(instance=instance)
        data = serializer.data

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(data['user'], self.user.pk)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['user'], self.user.pk)
        self.assertEqual(data['address'], '1 Y Street')
        self.assertEqual(data['notification_time'], '1h'),
        self.assertEqual(float(data['price']), float(120))

        expected_apple_order = {
            'item': self.ordered_apples.item.id,
            'quantity': self.ordered_apples.quantity
        }

        expected_pear_order = {
            'item': self.ordered_pears.item.id,
            'quantity': self.ordered_pears.quantity
        }
        self.assertIn(expected_apple_order, data['orders'])
        self.assertIn(expected_pear_order, data['orders'])

        
class PromocodeSerializerTestCase(BaseModelTestCase):

    def test_valid_serialization(self):
        instance = self.promocode
        serializer = PromocodeSerializer(instance=instance)
        data = serializer.data

        self.assertEqual(data['id'], self.promocode.pk)
        self.assertEqual(data['code'], 'l0DeUi')
        self.assertEqual(data['sale_percentage'], 3)
        self.assertEqual(data['is_active'], True)
        self.assertEqual(data['summarizes_with_other_sales'], False)
        self.assertIn('detail_promocode_url', data)

    
    def test_get_detail_url(self):
        instance = self.promocode
        request = self.request_factory.get(reverse('admin-promocode', kwargs={'pk': instance.pk}))
        serializer = PromocodeSerializer(instance=instance, context={'request': request})
        detail_promocode_url = serializer.data['detail_promocode_url']
        expected_url = '1'

        self.assertEqual(detail_promocode_url, f'http://testserver/api/admin/promocodes/{instance.pk}/')


# Views Tests
class AdminStoreBaseViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

        self.store_data = {
            'name': 'Admin2',
            'cashback_access_from': 300,
            'cashback_percentage': 3
        }


    def test_get_stores(self):
        StoreBase.objects.create()
        response = self.client.get(reverse('admin-store-settings'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Admin')
    

    def test_create(self):
        response = self.client.post(reverse('admin-store-settings'), self.store_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StoreBase.objects.count(), 1)
        self.assertEqual(StoreBase.objects.get().name, 'Admin2')
    

    def test_create_store_invalid_data(self):
        test_data = {
            'name': '',
            'cashback_access_from': -100,
            'cashback_percentage': 200
        }

        response = self.client.post(reverse('admin-store-settings'), test_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(StoreBase.objects.count(), 0)


    def test_non_admin_access(self):
        user = User.objects.create_user(
            username='user',
            email='user@gmail.com',
            password='userpass'
        )

        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('admin-store-settings'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminStoreBaseSingleViewTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = 'admin-detail-store-settings'

        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )

        self.client.login(username='admin', password='adminpass')

        self.store = StoreBase.objects.create(
            name='Admin',
            cashback_access_from=300,
            cashback_percentage=3
        )


    def test_get_store(self):
        response = self.client.get(reverse(self.url, kwargs={'pk': self.store.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Admin')

    
    def test_update_store(self):
        update_data = {'cashback_access_from': 250}
        response = self.client.put(reverse(self.url, kwargs={'pk': self.store.pk}), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.store.refresh_from_db()
        self.assertEqual(float(response.data['cashback_access_from']), float(update_data['cashback_access_from']))

    
    def test_delete_store(self):
        self.notAdminStore = StoreBase.objects.create(
            name='Additional',
            cashback_access_from=300,
            cashback_percentage=3
        )
        response = self.client.delete(reverse(self.url, kwargs={'pk': self.notAdminStore.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StoreBase.objects.count(), 1)


    def test_delete_admin_store(self):
        response = self.client.delete(reverse(self.url, kwargs={'pk': self.store.pk}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(StoreBase.objects.count(), 1)
        self.assertEqual(StoreBase.objects.get().name, 'Admin')

    
    def test_non_admin_access(self):
        user = User.objects.create_user(
            username='user',
            email='user@gmail.com',
            password='userpass'
        )

        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse(self.url, kwargs={'pk': self.store.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminProductsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = 'admin-products-list'
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

        self.product_data = {
            'name': 'Apple',
            'description': 'Some desc',
            'price': 140.20,
            'discount_percentage': 3
        }
    

    def test_create_product(self):
        response = self.client.post(reverse(self.url), data=self.product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Products.objects.count(), 1)
        self.assertEqual(response.data['name'], self.product_data['name'])
    

    def test_get_products(self):
        self.apple = Products.objects.create(
            **self.product_data
        )
        response = self.client.get(reverse(self.url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], self.product_data['name'])


    def test_non_admin_access(self):
        user = User.objects.create_user(
            username='user',
            email='user@gmail.com',
            password='userpass'
        )

        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse(self.url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        

class PublicProductViewSetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = 'product-list'

        self.product_data = {
            'name': 'Apple',
            'description': 'Some desc',
            'price': 140.20,
            'discount_percentage': 3
        }

        self.product = Products.objects.create(**self.product_data)
    

    def test_get_products(self):
        response = self.client.get(reverse(self.url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], self.product_data['name'])
        self.assertEqual(len(response.data), 1)
      
        
class CartItemViewSetTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = 'cart-list'

        user = User.objects.create_user(
            username='user',
            email='user@gmail.com',
            password='userpass'
        )

        self.client.login(username='user', password='userpass')

        self.product = Products.objects.create(
            name = 'Apple',
            description = 'Some desc',
            price = 140.20,
            discount_percentage = 3
        )

        self.cart_item_data = {
            'item': self.product.id,
            'quantity': 2
        }
    
    def test_create_cart_item(self):
        response = self.client.post(reverse(self.url), self.cart_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, self.cart_item_data['quantity'])
    

    def test_increase_current_cart_item(self):
        self.client.post(reverse(self.url), self.cart_item_data)

        self.new_cart_item_data = {
            'item': self.product.id,
            'quantity': 3
        }

        response = self.client.post(reverse(self.url), self.new_cart_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, 5)
    

    def test_decrease_cart_item(self):
        self.client.post(reverse(self.url), self.cart_item_data)

        self.new_cart_item_data = {
            'item': self.product.id,
            'quantity': -1
        }

        response = self.client.post(reverse(self.url), self.new_cart_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, 1)
    

    def test_decrease_more_than_0_cart_item(self):
        self.client.post(reverse(self.url), self.cart_item_data)

        self.new_cart_item_data = {
            'item': self.product.id,
            'quantity': -40
        }

        response = self.client.post(reverse(self.url), self.new_cart_item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 0)
    

    def test_delete_cart_item(self):
        self.retrive_url = 'cart-detail'
        self.client.post(reverse(self.url), self.cart_item_data)
        self.cart_item = CartItem.objects.get()

        response = self.client.delete(reverse(self.retrive_url, kwargs={'pk': self.cart_item.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)
    

    def test_retrive_cart_item(self):
        self.client.post(reverse(self.url), self.cart_item_data)
        self.cart_item = CartItem.objects.get()

        response = self.client.get(reverse(self.url), kwargs={'pk': self.cart_item.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['item'], self.cart_item.pk)
    

class OneProductPublicViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = 'detail-product'

        self.product_data = {
            'name': 'Apple',
            'description': 'Some desc',
            'price': 140.20,
            'discount_percentage': 3
        }

    
        self.product = Products.objects.create(
            **self.product_data
        )
    

    def test_retrieve_product(self):
        response = self.client.get(reverse(self.url, kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product_data['name'])
        self.assertEqual(response.data['description'], self.product_data['description'])
        self.assertEqual(float(response.data['price']), float(self.product_data['price']))
        self.assertEqual(response.data['discount_percentage'], self.product_data['discount_percentage'])
    

    def test_retrive_not_product(self):
        response = self.client.get(reverse(self.url, kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserRegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = 'regisrtation'

        self.user = {
            'username': 'TestUsername', 
            'first_name': 'TestName', 
            'last_name': 'TestSurname',
            'email': 'test@gmail.com',
            'password': 'testpass1',
            'phone': '+375297878787'
        }

    def test_user_creation(self):
        response = self.client.post(reverse(self.url), self.user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username=self.user['username'])
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertIsNotNone(profile.token)

    
    def test_user_invalid_creation(self):
        invalid_data = {
            'username': 'TestUsername', 
            'first_name': 'TestName', 
            'last_name': 'TestSurname',
            'email': 'not_a_valid_email',
            'password': 'testpass1'
        }

        response = self.client.post(reverse(self.url), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRegistrationTokenComfirmationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = 'regisrtation'
        self.confirmation_url = 'confirmation'

        self.user_data = {
            'username': 'TestUsername', 
            'first_name': 'TestName', 
            'last_name': 'TestSurname',
            'email': 'test@gmail.com',
            'password': 'testpass1',
            'phone': '+375297878787'
        }

        # self.user = User.objects.create_user(
        #     username = 'TestUsername', 
        #     first_name = 'TestName', 
        #     last_name = 'TestSurname',
        #     email = 'test@gmail.com',
        #     password = 'testpass1',
        # )

        # self.profile = Profile.objects.create(
        #     user = self.user,

        # )
    
    def test_full_registration_cycle(self):
        response = self.client.post(reverse(self.registration_url), self.user_data)
        user = User.objects.get(username=self.user_data['username'])
        profile = Profile.objects.get(user=user)

        response = self.client.get(reverse(self.confirmation_url, kwargs={'token': profile.token}))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        profile.refresh_from_db()
        self.assertIsNone(profile.token)
    

    def test_invalid_token_confirmation(self):
        response = self.client.post(reverse(self.registration_url), self.user_data)
        user = User.objects.get(username=self.user_data['username'])
        profile = Profile.objects.get(user=user)

        response = self.client.get(reverse(self.confirmation_url, kwargs={'token': 'invalid-token'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)

        profile.refresh_from_db()
        self.assertIsNotNone(profile.token)


class OrderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = 'order'

        self.store = StoreBase.objects.create()

        self.user = User.objects.create_user(
            username='TestUsername', 
            first_name='TestName', 
            last_name='TestSurname',
            email='test@gmail.com',
            password='testpass1'
            )
        self.client.force_authenticate(user=self.user)

        self.profile = Profile.objects.create(
            user = self.user,
            phone = '+375297878787',
            cashback = 0
        )

        self.apple = Products.objects.create(
            name = 'Apple',
            description = 'Some desc',
            price = 140.20,
            discount_percentage = 3
        )

        self.cart_item = CartItem.objects.create(
            user = self.user,
            item = self.apple,
            quantity = 5
        )

        self.active_promocode_summarizes = Promocodes.objects.create(
            code = '5bfpCH',
            sale_percentage = 10,
            is_active = True,
            summarizes_with_other_sales = True
        )
        
        self.active_promocode_not_summarizes = Promocodes.objects.create(
            code = 'x8V5hH',
            sale_percentage = 10,
            is_active = True,
            summarizes_with_other_sales = False
        )

        self.inactive_promocode = Promocodes.objects.create(
            code = 'WmT1c7',
            sale_percentage = 10,
            is_active = False,
            summarizes_with_other_sales = True
        )


    def test_successfull_order_creation_one(self):
        '''
            Valid data and active promo that summarizes. No cashback 
        '''

        current_promocode = self.active_promocode_summarizes

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
            'promocode': current_promocode
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity

        expected_final_price = round(cart_price * (1 - current_promocode.sale_percentage / 100), 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderedItems.objects.get().id, self.cart_item.item.pk)
        self.assertEqual(OrderedItems.objects.get().quantity, self.cart_item.quantity)
        self.assertEqual(CartItem.objects.count(), 0)
    

    def test_successfull_order_creation_two(self):
        '''
            Valid data and active promo that does not summarizes. No cashback 
        '''

        current_promocode = self.active_promocode_not_summarizes

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
            'promocode': current_promocode
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity

        expected_final_price = round(cart_price, 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)
    

    def test_successfull_order_creation_three(self):
        '''
            Valid data and inactive promo. No cashback 
        '''

        current_promocode = self.inactive_promocode

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
            'promocode': current_promocode
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity

        expected_final_price = round(cart_price, 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderedItems.objects.get().id, self.cart_item.item.pk)
        self.assertEqual(OrderedItems.objects.get().quantity, self.cart_item.quantity)
        self.assertEqual(CartItem.objects.count(), 0)


    def test_successfull_order_creation_four(self):
        '''
            Valid data and active promo. With cashback 
        '''
        self.profile.cashback = 350
        self.profile.save()

        current_promocode = self.active_promocode_summarizes

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
            'promocode': current_promocode
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity
        cashback = float(self.profile.cashback)

        expected_final_price = round(cart_price * (1 - current_promocode.sale_percentage / 100) - cashback, 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)
        

    def test_successfull_order_creation_five(self):
        '''
            Valid data and active promo that does not summarizes. With cashback 
        '''
        self.profile.cashback = 350
        self.profile.save()

        current_promocode = self.active_promocode_not_summarizes

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
            'promocode': current_promocode
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity

        expected_final_price = round(cart_price, 2)
        cashback = float(self.profile.cashback)

        expected_final_price = round(cart_price - cashback, 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)


    def test_successfull_order_creation_six(self):
        '''
            Valid data and active promo that summarizes. Too big cashback 
        '''

        self.profile.cashback = 900
        self.profile.save()

        current_promocode = self.active_promocode_summarizes

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
            'promocode': current_promocode
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity

        expected_final_price = round(cart_price * (1 - current_promocode.sale_percentage / 100), 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)


    def test_successfull_order_creation_seven(self):
        '''
            Valid data and no promo. No cashback 
        '''

        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        product_price = self.apple.get_final_price()
        quantity = self.cart_item.quantity
        cart_price = float(product_price) * quantity

        expected_final_price = round(cart_price, 2)
        self.assertEqual(float(Order.objects.get().price), expected_final_price)

        cashback_percentage = self.store.cashback_percentage
        expected_cashback = round(expected_final_price * cashback_percentage / 100, 2)
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.cashback), expected_cashback)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderedItems.objects.get().id, self.cart_item.item.pk)
        self.assertEqual(OrderedItems.objects.get().quantity, self.cart_item.quantity)
        self.assertEqual(CartItem.objects.count(), 0)
    

    def test_successfull_order_creation_eight(self):
        '''
            Invalid data and no promo. No cashback 
        '''

        test_data = {
            'address': '123 Test St',
            'notification_time': '2h',
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderedItems.objects.count(), 0)
        self.assertEqual(CartItem.objects.count(), 1)


    def test_non_authorized_access(self):
        self.client.logout()
        
        test_data = {
            'address': '123 Test St',
            'notification_time': '1h',
        }

        response = self.client.post(reverse(self.url), test_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CabinetViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = 'cabinet'

        self.user = User.objects.create_user(
            username='TestUsername', 
            first_name='TestName', 
            last_name='TestSurname',
            email='test@gmail.com',
            password='testpass1'
            )
        self.client.force_authenticate(user=self.user)

        self.profile = Profile.objects.create(
            user=self.user,
            phone = '+375297878787'
            )        

    def test_get_profile(self):
        response = self.client.get(reverse(self.url))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_info']['id'], self.user.id)
    

    def test_update_profile(self):
        update_data = {
            'is_subscribed': True,
        }
        response = self.client.patch(reverse(self.url), update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_subscribed)

    
    def test_denied_access(self):
        self.client.logout()
        response = self.client.get(reverse(self.url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    

class AdminPromocodesCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = 'admin-promocodes-create'

        self.user = User.objects.create_user(
            username='TestUsername', 
            first_name='TestName', 
            last_name='TestSurname',
            email='test@gmail.com',
            password='testpass1'
            )

        self.admin = User.objects.create_superuser(
            username='test_admin', 
            password='testpass1'
        )
        self.client.force_authenticate(user=self.admin)

        self.test_data = {
            'code': '1uDDeW',
            'sale_percentage': 10,
            'is_active': False,
            'summarizes_with_other_sales': False
        }
    
    def test_create_promocode(self):

        response = self.client.post(reverse(self.url), self.test_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Promocodes.objects.count(), 1)
        self.assertEqual(response.data['code'], self.test_data['code'])
    

    def test_invalid_data_create_promocode(self):
        self.test_data = {
            'code': '1uDDeWO',
            'sale_percentage': 10,
            'is_active': False,
            'summarizes_with_other_sales': False
        }

        response = self.client.post(reverse(self.url), self.test_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Promocodes.objects.count(), 0)
    

    def test_get_promocodes(self):

        promocode = Promocodes.objects.create(
            ** self.test_data
        )

        response = self.client.get(reverse(self.url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['code'], self.test_data['code'])
    

    def non_admin_access(self):
        self.client.logout()
        self.client.force_authenticate(user=self.user) 

        response = self.client.get(reverse(self.url))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPromocodeViewTestCase(TestCase):
    
    def setUp(self):

        self.client = APIClient()
        self.url = 'admin-promocode'

        self.user = User.objects.create_user(
            username='TestUsername', 
            first_name='TestName', 
            last_name='TestSurname',
            email='test@gmail.com',
            password='testpass1'
            )

        self.admin = User.objects.create_superuser(
            username='test_admin', 
            password='testpass1'
        )
        self.client.force_authenticate(user=self.admin)

        self.test_data = {
            'code': '1uDDeW',
            'sale_percentage': 10,
            'is_active': False,
            'summarizes_with_other_sales': False
        }

        self.promocode = Promocodes.objects.create(
            ** self.test_data
        )

    
    def test_retrive_success(self):
        response = self.client.get(reverse(self.url, kwargs={'pk': self.promocode.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], self.test_data['code'])
        self.assertIn('detail_promocode_url', response.data)
    

    def test_retrive_nonexisting(self):
        response = self.client.get(reverse(self.url, kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    

    def test_patch_success(self):
        patch_data = {
            'sale_percentage': 5
        }

        response = self.client.patch(reverse(self.url, kwargs={'pk': self.promocode.pk}), patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sale_percentage'], patch_data['sale_percentage'])

    
    def test_patch_invalid_data(self):
        patch_data = {
            'code': 'sdjfvjbvdflsj'
        }

        response = self.client.patch(reverse(self.url, kwargs={'pk': self.promocode.pk}), patch_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Promocodes.objects.get().code, self.test_data['code'])

    
    def test_delete_success(self):
        response = self.client.delete(reverse(self.url, kwargs={'pk': self.promocode.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    
    def test_delete_nonexisting(self):
        response = self.client.delete(reverse(self.url, kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(response.data), 1)

    
    def test_non_admin_access(self):
        self.client.logout()
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(reverse(self.url, kwargs={'pk': self.promocode.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)