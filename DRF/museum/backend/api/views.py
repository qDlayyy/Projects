import datetime
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render


from . import models, serializers

from .tasks import send_verification_email


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_verification_obj = models.EmailVerification.objects.create(user=user)
        token = email_verification_obj.token
        confirmation_link = self.request.build_absolute_uri() + str(token)
        user_email = user.email

        send_verification_email(user_email=user_email, link=confirmation_link)

        return Response({'detail': 'Check your email & follow the link to finally create the email'}, status=status.HTTP_201_CREATED)

user_registration_view = UserRegistrationView.as_view()


class UserConfirmationView(generics.GenericAPIView):
    def get(self, request, token):
        try:
            user_profile = models.EmailVerification.objects.get(token=token)
            if user_profile.created_at < datetime.datetime.now() + datetime.timedelta(hours=24):
                user = user_profile.user
                user.is_active = True
                user.save()

                user_profile.token = None
                user_profile.save()

                return Response({'detail': 'Your account has been successfully created. Now you can log in.'}, status=status.HTTP_200_OK)
            
            else:
                user = user_profile.user
                user.delete()

                return Response({'detail': 'Unfortunately your verification token has expired. You have only 24 hours to confirm creation after the verificaton email is sent. Try again.'}, status=status.HTTP_410_GONE)

        
        except models.EmailVerification.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

user_confirmation_view = UserConfirmationView.as_view()


        



class MuseumsListView(generics.ListAPIView):
    queryset = models.Museums.objects.all()
    serializer_class = serializers.MuseumsListSerializer

museum_list_view = MuseumsListView.as_view()

class MuseumsRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.MuseumRetriveSerializer

    def get_object(self):
        museum_obj = models.Museums.objects.get(pk=self.kwargs.get('pk'))

        return museum_obj

    
    def get(self, request, *args, **kwargs):
        museum = self.get_object()
        serializer = self.get_serializer(museum)

        return Response(serializer.data, status=status.HTTP_200_OK)

museum_retrive_view = MuseumsRetriveView.as_view()


class AuthorsListView(generics.ListAPIView):
    queryset = models.Authors.objects.all()
    serializer_class = serializers.AuthorsSerializer

    def get_serializer(self, *args, **kwargs):
        only_fields = ['name', 'surname', 'retrive_url']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)

authors_list_view = AuthorsListView.as_view()


class AuthorsRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.AuthorsSerializer

    def get_serializer(self, *args, **kwargs):
        only_fields = ['retrive']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)
    
    
    def get_object(self):
        author_obj = models.Authors.objects.get(pk=self.kwargs.get('pk'))

        return author_obj
    

    def get(self, request, *args, **kwargs):
        author = self.get_object()
        serializer = self.get_serializer(author)

        return Response(serializer.data, status=status.HTTP_200_OK)

authors_retrive_view = AuthorsRetriveView.as_view()


class ExhibitsListView(generics.ListAPIView):
    queryset = models.Exhibits.objects.all()
    serializer_class = serializers.ExhibitsSerializer

    
    def get_serializer(self, *args, **kwargs):
        only_fields = ['name', 'author', 'museum', 'retrive_url']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)

exhibits_list_view = ExhibitsListView.as_view()


class ExhibitsRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.ExhibitsSerializer

    def get_serializer(self, *args, **kwargs):
        only_fields = ['retrive']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)
    

    def get_object(self):
        exhibit_obj = models.Exhibits.objects.get(pk=self.kwargs.get('pk'))

        return exhibit_obj
    

    def get(self, request, *args, **kwargs):
        exhibit = self.get_object()
        serializer = self.get_serializer(exhibit)

        return Response(serializer.data, status=status.HTTP_200_OK)

exhibits_retrive_view = ExhibitsRetriveView.as_view()