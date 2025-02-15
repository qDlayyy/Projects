from rest_framework import serializers
from .models import User, Cinemas, Actors, Directors, Genres, Films, Sessions, Tickets
from rest_framework.reverse import reverse


class UserRegistrationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.is_active = False
        user.save()

        return user


class CinemasSerializer(serializers.ModelSerializer):
    retrive_cinema_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cinemas
        fields = [
            'name',
            'address',
            'retrive_cinema_url'
        ]

    
    def get_retrive_cinema_url(self, obj):
        request = self.context.get('request')

        if request is None:
            return None

        return reverse(viewname='cinema-detail', kwargs={'pk': obj.pk}, request=request)
    

class RetriveCinemaSerializer(CinemasSerializer):

    available_sessions = serializers.SerializerMethodField()
    
    class Meta(CinemasSerializer.Meta):
        fields = [
            field for field in CinemasSerializer.Meta.fields if field != 'retrive_cinema_url'
        ] + ['available_sessions']

    
    def get_available_sessions(self, obj):
        sessions = Sessions.objects.filter(pk=obj.pk).all()

        if not sessions:
            return None

        return SessionsSerializer(sessions, many=True, context=self.context).data


class SessionsSerializer(serializers.ModelSerializer):
    retrive_session_url = serializers.SerializerMethodField(read_only=True)
    cinema_name = serializers.SerializerMethodField(read_only=True)
    film_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Sessions
        fields = [
            'name',
            'cinema_name',
            'film_name',
            'time',
            'retrive_session_url'
        ]
    

    def get_retrive_session_url(self, obj):
        request = self.context.get('request')

        if request is None:
            return None
        
        return reverse(viewname='sessions-detail', kwargs={'pk': obj.pk}, request=request)


    def get_cinema_name(self, obj):
        return obj.cinema.name if obj.cinema else None
    

    def get_film_name(self, obj):
        return obj.film.name if obj.film else None
    

class RetriveSessionSerializer(SessionsSerializer):

    film_data = serializers.SerializerMethodField()
    tickets_booking_url = serializers.SerializerMethodField()
    available_tickets = serializers.SerializerMethodField()

    class Meta(SessionsSerializer.Meta):
        fields = [
            field for field in SessionsSerializer.Meta.fields if field not in ['retrive_session_url', 'film_name']
        ] + ['film_data', 'available_tickets', 'tickets_booking_url']


    def get_film_data(self, obj):
        film = Films.objects.get(pk=obj.pk)

        return FilmRetriveSerializer(film, context=self.context).data

    
    def get_tickets_booking_url(self, obj):
        request = self.context.get('request')

        if not request:
            return None
        
        return reverse(viewname='booking', kwargs={'pk': obj.pk}, request=request)


    def get_available_tickets(self, obj):
        tickets = Tickets.objects.filter(session=obj, is_available=True)

        if not tickets:
            return None
        
        return TicketSerializer(tickets, many=True, context=self.context).data


class FilmsSerializer(serializers.ModelSerializer):
    retrive_film_url = serializers.SerializerMethodField()
    genres_data = serializers.SerializerMethodField()
    director_data = serializers.SerializerMethodField()

    class Meta:
        model = Films
        fields = [
            'name',
            'director_data',
            'duration_mins',
            'genres_data',
            'image',
            'retrive_film_url'
        ]
    
    def get_director_data(self, obj):
        director = obj.director
        
        if not director:
            return None
        
        return DirectorSerializer(director, only_fields=['name', 'surname', 'retrive_director_url'], context=self.context).data
    

    def get_genres_data(self, obj):
        genres = obj.genres.all()
        
        if not genres:
            return None
        
        return [genre.genre for genre in genres]
        
    
    def get_retrive_film_url(self, obj):
        request = self.context.get('request')

        if request is None:
            return None
        
        return reverse(viewname='film-detail', kwargs={'pk': obj.pk}, request=request)
    

class FilmRetriveSerializer(FilmsSerializer):
    actors_data = serializers.SerializerMethodField()

    class Meta(FilmsSerializer.Meta):
        fields = [
            field for field in FilmsSerializer.Meta.fields if field != 'retrive_film_url'
        ] + ['actors_data']
    

    def get_actors_data(self, obj):
        actors = obj.actors

        if not actors:
            return None
        
        return ActorSerializer(actors, only_fields=['name', 'surname', 'retrive_actor_url'], many=True, context=self.context).data
        

class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = [
            'genre'
        ]
    

class DirectorSerializer(serializers.ModelSerializer):
    films = serializers.SerializerMethodField()
    retrive_director_url = serializers.SerializerMethodField()

    class Meta:
        model = Directors
        fields = [
            'name',
            'surname',
            'photo',
            'films',
            'retrive_director_url'
        ]
    

    def __init__(self, *args, **kwargs):
        only_fields = kwargs.pop('only_fields', None)
        super(DirectorSerializer, self).__init__(*args, **kwargs)

        if only_fields:
            for field_name in list(self.fields.keys()):
                if field_name not in only_fields:
                    self.fields.pop(field_name)
    

    def get_films(self, obj):
        films = Films.objects.filter(director=obj).all()

        if not films:
            return None
        
        return FilmsSerializer(films, many=True, context=self.context).data
    

    def get_retrive_director_url(self, obj):
        request = self.context.get('request')

        if not request:
            return None
        
        return reverse(viewname='directors-detail', kwargs={'pk': obj.pk}, request=request)


class ActorSerializer(serializers.ModelSerializer):

    retrive_actor_url = serializers.SerializerMethodField()
    films = serializers.SerializerMethodField()

    class Meta:
        model = Actors
        fields = [
            'name',
            'surname',
            'photo',
            'films',
            'retrive_actor_url'
        ]
    
    def __init__(self, *args, **kwargs):
        only_fields = kwargs.pop('only_fields', None)
        super(ActorSerializer, self).__init__(*args, **kwargs)

        if only_fields:
            for field_name in list(self.fields.keys()):
                if field_name not in only_fields:
                    self.fields.pop(field_name)

    
    def get_films(self, obj):
        films = obj.films_by_actor

        if not films:
            return None
        
        return FilmsSerializer(films, many=True, context=self.context).data
    

    def get_retrive_actor_url(self, obj):
        request = self.context.get('request')

        if not request:
            return None
        
        return reverse(viewname='actors-detail', kwargs={'pk': obj.pk}, request=request)
    

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = [
            'id',
            'is_available',
            'seat'
        ]