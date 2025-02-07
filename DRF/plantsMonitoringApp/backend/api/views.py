from django.shortcuts import render
from .models import Profile, Plants, Tips, Gallery, Diary
from .serializers import UserRegistration, PlantsSerializer, TipsSerializer, GallerySerializer, DiarySerializer, PlantRetriveSerializator
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.utils.crypto import get_random_string
from rest_framework.exceptions import PermissionDenied


class AdminPlantsViewSet(viewsets.ModelViewSet):
    queryset = Plants.objects.all()
    serializer_class = PlantsSerializer
    permission_classes = [IsAdminUser]


class AdminTips(viewsets.ModelViewSet):
    queryset = Tips.objects.all()
    serializer_class = TipsSerializer
    permission_classes = [IsAdminUser]


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistration

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = get_random_string(32)
        profile = Profile.objects.get(user=user)
        profile.token = token
        profile.save()

        self.send_email(user=user, token=token)

        comfirmation_link = self.request.build_absolute_uri() + token

        return Response({
            'detail': 'The email was sent successfully.',
            'instructions': 'Follow the link to create an account.', 
            'temprorary email': f'{comfirmation_link}'}, 
            status=status.HTTP_201_CREATED)


    def send_email(self, user,  token):
        pass

user_register_view = UserRegistrationView.as_view()


class UserRegistrationComfirmationView(generics.GenericAPIView):
    
    def get(self, request, token):
        try:
            profile = Profile.objects.get(token=token)
            user = profile.user
            user.is_active = True
            user.save()

            profile.token = None
            profile.save()

            return Response({
                'detail': 'Your account has been activated successfully.',
                'instructions': 'No automatic Log in for security reasons. Log in with password by our own.'
                },
                status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
user_confirmation_view = UserRegistrationComfirmationView.as_view()


class AllPlantsView(generics.ListCreateAPIView):
    queryset = Plants.objects.all()
    serializer_class = PlantsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = Profile.objects.get(user=request.user)
        serializer.save(profile=profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED) 

all_plants_view = AllPlantsView.as_view()


class RetrivePlantView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlantRetriveSerializator
    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self):
        plant_id = self.kwargs.get("pk")
        plant = Plants.objects.get(pk=plant_id)

        return plant

    
    def update(self, request, *args, **kwargs):
        plant = self.get_object()
        profile = Profile.objects.get(user=request.user)

        if plant.profile != profile:
            raise PermissionDenied('You cannot update other users\' plants.')
        
        serializer = self.get_serializer(plant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def get(self, request, *args, **kwargs):
        plant = self.get_object()
        serializer = self.get_serializer(plant)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def destroy(self, request, *args, **kwargs):
        plant = self.get_object()
        profile = Profile.objects.get(user=request.user)

        if plant.profile != profile:
            raise PermissionDenied('You cannot destroy other users\' plants.')
        
        plant.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

retrive_plant_view = RetrivePlantView.as_view()


class DiaryViewSet(viewsets.ModelViewSet):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = Profile.objects.get(user=request.user)
        serializer.save(profile=profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    
    def update(self, request, *args, **kwargs):
        plant = self.get_object()
        
        profile = Profile.objects.get(user=request.user)
        if plant.profile != profile:
            raise PermissionDenied('You cannot update other users\' dairy notes.')
        
        selrializer = self.get_serializer(plant, data=request.data, partial=True)
        selrializer.is_valid(raise_exception=True)
        selrializer.save()

        return Response(selrializer.data, status=status.HTTP_200_OK)
    

    def destroy(self, request, *args, **kwargs):
        plant = self.get_object()

        profile = Profile.objects.get(user=request.user)
        if plant.profile != profile:
            raise PermissionDenied('You cannot destroy other users\' dairy notes.')
        
        plant.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class GalleryView(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [IsAuthenticated]


    def update(self, request, *args, **kwargs):
        gallery = self.get_object()

        profile = Profile.objects.get(user=request.user)
        if gallery.plant.profile != profile:
            raise PermissionDenied('You cannot update other users\' galleries.')

        seriaizer = self.get_serializer(gallery, data=request.data, partial=True)
        seriaizer.is_valid(raise_exception=True)

        seriaizer.save()

        return Response(seriaizer.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        gallery = self.get_object()

        profile = Profile.objects.get(user=request.user)
        if gallery.plant.profile != profile:
            raise PermissionDenied('You cannot destoroy other users\' galleries.')
        
        gallery.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

