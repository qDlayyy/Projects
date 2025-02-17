from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Profile, Products, CartItem, Order, OrderedItems, Promocodes, StoreBase
from django.contrib.auth.models import User


class StoreBaseSerializer(serializers.ModelSerializer):

    update_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StoreBase
        fields = [
            'id',
            'update_url',
            'name',
            'cashback_access_from',
            'cashback_percentage',
        ]
    

    def get_update_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return reverse('admin-detail-store-settings', kwargs={'pk': obj.pk}, request=request)
    
    '''
        Поскольку этот валидатор будет работать только на изменении уже созданных наборов настроек,
        то никто не помешает админу создать настройки с отрицательными значениями и использовать их.
        Поэтому валидатор добавлен к модели.
    '''
    # def validate_cashback_percentage(self, attrs):
    #     if 0 < attrs < 100:
    #         return attrs
    #     else:
    #         raise serializers.ValidationError(f'Default cashback canot be {attrs}.')
        

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)


class ProfileSerializer(serializers.ModelSerializer):

    user_info = UserSerializer(source='user', read_only=True)
    user_phone = serializers.CharField(source='phone', read_only=True)
    user_cashback = serializers.DecimalField(source='cashback', read_only=True, max_digits=7, decimal_places=2)
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = Profile
        fields = [
            'user_info',
            'user_phone',
            'is_subscribed',
            'user_cashback',
        ]


class ProductsSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField(read_only=True)
    detail_product_url = serializers.SerializerMethodField(read_only=True)
    cart_add_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Products
        fields = [
            'id',
            'detail_product_url',
            'cart_add_url',
            'name',
            'description',
            'price',
            'discount_percentage',
            'final_price',
        ]

    
    def get_final_price(self, obj):
        return obj.get_final_price()
    

    def get_detail_product_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse('detail-product', kwargs={'pk': obj.pk}, request=request)


    def get_cart_add_url(self,obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse('add-to-cart', kwargs={'pk': obj.pk}, request=request)
    

class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id',
            'name',
            'item',
            'quantity'
        ]

    def get_name(self, obj):
        if isinstance(obj, CartItem):
            return obj.item.name if obj.item else None
        return None


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=13)

    class Meta:
        model = User
        fields =[
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'phone'
        ]
    

    def create(self, validated_data):
        phone = validated_data.pop('phone')

        user = User.objects.create(
            username = validated_data.get('username'),
            first_name = validated_data.get('first_name'),
            last_name = validated_data.get('last_name'),
            email = validated_data.get('email')
        )

        user.set_password(validated_data.get('password'))
        user.is_active = False
        user.save()

        Profile.objects.create(
            user = user,
            phone = phone
        )

        return user


class OrderedItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedItems
        fields = [
            'item',
            'quantity'
        ]
    

class OrderConfirmationSerilizer(serializers.ModelSerializer):
    orders = OrderedItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'user',
            'email',
            'orders',
            'address',
            'notification_time',
            'price'
        ]
    

    def create(self, validated_data):
        orders_data = validated_data.pop('orders')
        
        order = Order.objects.create(**validated_data)
    
        for order_item_data in orders_data:
            order_item = OrderedItems.objects.create(user=validated_data.get('user'), **order_item_data)

            order.orders.add(order_item)

        CartItem.objects.filter(user=validated_data.get('user')).delete()

        return order


class PromocodeSerializer(serializers.ModelSerializer):

    detail_promocode_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Promocodes
        fields = [
            'id',
            'detail_promocode_url',
            'code',
            'sale_percentage',
            'is_active',
            'summarizes_with_other_sales',
        ]
    
    def get_detail_promocode_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse('admin-promocode', kwargs={'pk': obj.pk}, request=request)