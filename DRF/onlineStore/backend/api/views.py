from django.shortcuts import render
from .models import Profile, Products, CartItem, Promocodes, StoreBase
from .serializers import ProductsSerializer, CartItemSerializer, UserRegisterSerializer, OrderConfirmationSerilizer, ProfileSerializer, PromocodeSerializer, StoreBaseSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from rest_framework.views import APIView

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


class AdminStoreBaseView(generics.ListCreateAPIView):
    queryset = StoreBase.objects.all()
    serializer_class = StoreBaseSerializer
    permission_classes = [IsAdminUser]

admin_store_base_view = AdminStoreBaseView.as_view()


class AdminStoreBaseSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StoreBase.objects.all()
    serializer_class = StoreBaseSerializer
    permission_classes = [IsAdminUser]


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.name == 'Admin':
            return Response(
                {'detail':'This item cannot be deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

admin_store_base_view_single = AdminStoreBaseSingleView.as_view()


class AdminProductsViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [IsAdminUser]


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return CartItem.objects.filter(user=user)

        return CartItem.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        item = serializer.validated_data.get('item')
        existing_cart_item = CartItem.objects.filter(user=user, item=item).first()
        if existing_cart_item:
            existing_cart_item.quantity += serializer.validated_data.get('quantity')
            if existing_cart_item.quantity <= 0:
                existing_cart_item.delete()
                return None
            existing_cart_item.save()
            return existing_cart_item
        
        else:
            serializer.save(user=user)
            return serializer.data

    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)
    

class CartAddView(generics.CreateAPIView):
    # serializer_class = CartItemSerializer
    # permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     user = self.request.user

    #     item = serializer.validated_data.get('item')
    #     existing_cart_item = CartItem.objects.filter(user=user, item=item).first()
    #     if existing_cart_item:
    #         existing_cart_item.quantity += serializer.validated_data.get('quantity')
    #         existing_cart_item.save()
    #         return Response(CartItemSerializer(existing_cart_item).data, status=status.HTTP_200_OK)
        
    #     else:
    #         serializer.save(user=user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    

    def post(self, request, pk, *args, **kwargs):
        product = Products.objects.get(pk=pk)
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            return Response({"detail": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(user=request.user, item=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return Response({"detail": "Product added to cart.", "product": product.name, "quantity": cart_item.quantity}, 
                        status=status.HTTP_201_CREATED)

add_to_cart = CartAddView.as_view()


class OneProductPublicView(generics.RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer

detail_product_public_view = OneProductPublicView.as_view()


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = get_random_string(length=32)
        user_profile = Profile.objects.get(user=user)
        user_profile.token = token
        user_profile.save()

        self.send_email(user, token)

        comfirmation_link = self.request.build_absolute_uri() + token

        return Response({
            'detail': 'The email was sent successfully.',
            'instructions': 'Follow the link to create an account.'},
            status=status.HTTP_201_CREATED)


    def send_email(self, user, token):
        current_site = self.request.build_absolute_uri()
        comfirmation_link = current_site + token
        mail_subject = 'Account activation'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        message = render_to_string('activate_template.html', {
        'user': user,
        'domain': current_site,
        'uid': uid,
        'link': comfirmation_link,
        })

        email = EmailMessage(
            mail_subject, 
            message, 
            to=[user.email]
        )

        email.send()
        

user_register_view = UserRegisterView.as_view()


class UserRegistrationTokenComfirmation(generics.GenericAPIView):
    def get(self, request, token):
        try:
            user_profile = Profile.objects.get(token=token)
            user = user_profile.user
            user.is_active = True
            user.save()

            user_profile.token = None
            user_profile.save()

            return Response({
                'detail': 'Your account has been activated successfully.',
                'instructions': 'No automatic Log in for security reasons. Log in with password by our own.'
                },
                status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

user_register_token_confirmation = UserRegistrationTokenComfirmation.as_view()


class OrderView(generics.CreateAPIView):
    serializer_class = OrderConfirmationSerilizer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_data = CartItem.objects.filter(user=request.user)
        if not cart_data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        promocode = request.data.get('promocode')
        promocode_summarizes_with_other_sales = False

        if promocode is not None:
            validated_promocode = Promocodes.objects.filter(code=promocode, is_active=True).first()
            
            if validated_promocode is not None:
                sale_percentage = validated_promocode.sale_percentage
                promocode_summarizes_with_other_sales = validated_promocode.summarizes_with_other_sales
            else:
                sale_percentage = 0
        
        else:
            sale_percentage = 0
        
        final_price = 0
        for cart_item in cart_data:
            final_price += cart_item.item.get_final_price() * cart_item.quantity
        
        if promocode_summarizes_with_other_sales:
            final_price = float(final_price) * (1 - sale_percentage / 100)
        

        store_settings = StoreBase.objects.filter(name='Admin').first()
        cashback_access_point = float(store_settings.cashback_access_from)
        cashback_percentage = float(store_settings.cashback_percentage)

        user_profile = Profile.objects.filter(user=self.request.user).first()
        cashback = float(user_profile.cashback)
        
        final_price = float(final_price)

        if cashback > cashback_access_point and float(final_price) - cashback > 0:
            final_price -= cashback
            user_profile.cashback = 0
            user_profile.save()

        final_price = round(final_price, 2)

        orders_data = []
        for item in cart_data:
            orders_data.append({
                'item': item.item.id,
                'quantity': item.quantity
            })
        
        order_data = {
            'user': request.user.id,
            'email': request.user.email,
            'orders': orders_data,
            'address': request.data.get('address'),
            'notification_time': request.data.get('notification_time'),
            'price': final_price
        }

        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        user_profile.cashback = round(float(final_price) * cashback_percentage / 100, 2)
        user_profile.save()
        return Response(status=status.HTTP_201_CREATED)

order_view = OrderView.as_view()


class CabinetView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
    
    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

cabinet_view = CabinetView.as_view()


class AdminPromocodesCreate(generics.ListCreateAPIView):
    queryset = Promocodes.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = [IsAdminUser]

admin_promocodes_create = AdminPromocodesCreate.as_view()


class AdminPromocodeView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promocodes.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = [IsAdminUser]

admin_single_promocode_view = AdminPromocodeView.as_view()
