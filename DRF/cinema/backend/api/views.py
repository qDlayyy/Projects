from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from . import serializers, models


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = models.EmailVerification.objects.create(user=user)
        current_url = self.request.build_absolute_uri()
        new_url = current_url.replace('register', 'confirmation')

        link = f'{new_url}?token={token.token}'
        print(link)

        send_mail(
            'Verify your account',
            f'Follow the link to confirm the account creation: {link}',
            'Best Regards, Team!',
            recipient_list=[user.email],
            fail_silently = False
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

user_registration_view = UserRegistrationView.as_view()
    

class UserRegistrationConfirmationView(APIView):
    def get(self, request):
        token = request.GET.get('token')

        try:
            verification_token = models.EmailVerification.objects.get(token=token)
            if verification_token.is_valid():
                user = verification_token.user
                user.is_active = True
                user.save()
                verification_token.delete()
                
                return Response({"success": "Email verified successfully!"}, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Token is not valid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        
        except:
                return Response({"error": "Token does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
user_confirmation_view = UserRegistrationConfirmationView.as_view()


class CinemasListView(generics.ListAPIView):
     queryset = models.Cinemas.objects.all()
     serializer_class = serializers.CinemasSerializer
    
cinemas_list_view = CinemasListView.as_view()


class CinemaRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.RetriveCinemaSerializer

    def get_object(self):
        cinema = models.Cinemas.objects.get(pk=self.kwargs.get('pk'))

        return cinema
    

    def get(self, request, *args, **kwargs):
        cinema = self.get_object()
        serializer = self.get_serializer(cinema)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
cinema_retrive_view = CinemaRetriveView.as_view()


class SessionsListView(generics.ListAPIView):
    queryset = models.Sessions.objects.all()
    serializer_class = serializers.SessionsSerializer

sessions_list_view = SessionsListView.as_view()


class SessionRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.RetriveSessionSerializer

    def get_object(self):
        session = models.Sessions.objects.get(pk=self.kwargs.get('pk'))

        return session
    

    def get(self, request, *args, **kwargs):
        session = self.get_object()
        serializer = self.get_serializer(session)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
session_retrive_view = SessionRetriveView.as_view()


class FilmsListView(generics.ListAPIView):
    queryset = models.Films.objects.all()
    serializer_class = serializers.FilmsSerializer

films_list_view = FilmsListView.as_view()


class FilmRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.FilmRetriveSerializer

    def get_object(self):
        film = models.Films.objects.get(pk=self.kwargs.get('pk'))
        return film
    
    
    def get(self, request, *args, **kwargs):
        film = self.get_object()
        serializer = self.get_serializer(film)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
film_retrive_view = FilmRetriveView.as_view()


class DirectorsListView(generics.ListAPIView):
    queryset = models.Directors.objects.all()
    serializer_class = serializers.DirectorSerializer

    def get_serializer(self, *args, **kwargs):
        only_fields = ['name', 'surname', 'photo', 'retrive_director_url']
        kwargs['only_fields']= only_fields

        return super().get_serializer(*args, **kwargs)

directors_list_view = DirectorsListView.as_view()
    

class DirectorRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.DirectorSerializer

    def get_object(self):
        director = models.Directors.objects.get(pk=self.kwargs.get('pk'))

        return director
    

    def get_serializer(self, *args, **kwargs):
        only_fields = ['name', 'surname', 'photo', 'films']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)
    

    def get(self, request, *args, **kwargs):
        director = self.get_object()
        serializer = self.get_serializer(director)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
direcctor_retrive_view = DirectorRetriveView.as_view()


class ActorsListView(generics.ListAPIView):
    queryset = models.Actors.objects.all()
    serializer_class = serializers.ActorSerializer

    def get_serializer(self, *args, **kwargs):
        only_fields = ['name', 'surname', 'photo', 'retrive_actor_url']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)

actors_list_view = ActorsListView.as_view()


class ActorRetriveView(generics.RetrieveAPIView):
    serializer_class = serializers.ActorSerializer

    def get_object(self):
        actor = models.Actors.objects.get(pk=self.kwargs.get('pk'))
        
        return actor
    

    def get_serializer(self, *args, **kwargs):
        only_fields = ['name', 'surname', 'photo', 'films']
        kwargs['only_fields'] = only_fields

        return super().get_serializer(*args, **kwargs)
    

    def get(self, request, *args, **kwargs):
        actor = self.get_object()
        serializer = self.get_serializer(actor)

        # Если бы поля не изменялись бы динамически в ините сериализатора, то можно было бы определять их тут
        # serializer = self.get_serializer(director, context={'request': request})  
        # serializer.fields = {field: serializer.fields[field] for field in ['name', 'surname', 'photo'] if field in serializer.fields}

        return Response(serializer.data, status=status.HTTP_200_OK)

actor_retrive_view = ActorRetriveView.as_view()


class BookTicketsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        tickets_ids = request.data.get('tickets_ids', None)

        tickets = models.Tickets.objects.filter(pk__in=tickets_ids)
        
        if not tickets or len(tickets) != len(tickets_ids):
            return Response({'error': 'Some or all of the tickets are unreachable.'}, status=status.HTTP_400_BAD_REQUEST)

        booked_tickets = tickets.filter(is_available=False)
        
        if booked_tickets:
            return Response({'error': 'At least one of the tickets is booked'}, status=status.HTTP_400_BAD_REQUEST)
        
        tickets.update(is_available=False, user=request.user)
    

        return Response({'detail': 'Chosen tickets have been successfully booked'}, status=status.HTTP_200_OK)
    
book_tickets_view = BookTicketsView.as_view()