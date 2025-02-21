from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse

from . import models


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            'username',
            'email',
            'password'
        ]
        extra_kwargs = {
            'password':{'write_only': True}
        }

    
    def create(self, validated_data):
        user = models.User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.is_active = False
        user.save()

        return user


class MuseumsListSerializer(serializers.ModelSerializer):
    retrive_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Museums
        fields = [
            'id',
            'name',
            'address',
            'retrive_url'
        ]
    

    def get_retrive_url(self, obj):
        request = self.context.get('request')

        if not request:
            return None
        
        return reverse('museums-detail', kwargs={'pk': obj.pk}, request=request)


class MuseumRetriveSerializer(MuseumsListSerializer):
    exhibits = serializers.SerializerMethodField()

    class Meta(MuseumsListSerializer.Meta):
        fields = [field for field in MuseumsListSerializer.Meta.fields if field != 'retrive_url'] + [
            'exhibits'
        ]
    

    def get_exhibits(self, obj):
        exhibits_obj = models.Exhibits.objects.filter(museum=obj).all()

        if not exhibits_obj:
            return None
        
        return ExhibitsSerializer(exhibits_obj, many=True, context=self.context, only_fields=['name', 'author', 'retrive_url', 'photo']).data


class EraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Era
        fields = [
            'id',
            'name',
            'century_of_beginning',
            'century_of_ending'
        ]


class CaterorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Categories
        fields = [
            'id',
            'name'
        ]
    

class AuthorsSerializer(serializers.ModelSerializer):
    retrive_url = serializers.SerializerMethodField()
    era = serializers.SerializerMethodField()
    exhibits = serializers.SerializerMethodField()

    class Meta:
        model = models.Authors
        fields = [
            'id',
            'name',
            'surname',
            'era',
            'date_of_birth',
            'photo',
            'exhibits',
            'retrive_url'
        ]
    

    def __init__(self, *args, **kwargs):
        only_fields = kwargs.pop('only_fields', None)
        super(AuthorsSerializer, self).__init__(*args, **kwargs)

        if only_fields and 'retrive' in only_fields and len(only_fields) == 1:
            self.fields.pop('retrive_url')

        elif only_fields:
            for field_name in list(self.fields.keys()):
                if field_name not in only_fields:
                    self.fields.pop(field_name)


    def get_era(self, obj):
        era_obj = obj.era if obj else None

        if not era_obj:
            return None
        
        return EraSerializer(era_obj, context=self.context).data
    

    def get_exhibits(self, obj):
        exhibits_obj = models.Exhibits.objects.filter(author=obj).all()

        return ExhibitsSerializer(exhibits_obj, many=True, context=self.context, only_fields=['name', 'museum', 'retrive_url', 'photo']).data


    def get_retrive_url(self, obj):
        request = self.context.get('request')

        if not request:
            return None
        
        return reverse('authors-detail', kwargs={'pk': obj.pk}, request=request)


class ExhibitsSerializer(serializers.ModelSerializer):
    retrive_url = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    museum = serializers.SerializerMethodField()

    class Meta:
        model = models.Exhibits
        fields = [
            'id',
            'name',
            'author',
            'category',
            'museum',
            'photo',
            'retrive_url'
        ]
    
    def __init__(self, *args, **kwargs):
        only_fields = kwargs.pop('only_fields', None)

        super(ExhibitsSerializer, self).__init__(*args, **kwargs)

        if only_fields and 'retrive' in only_fields and len(only_fields) == 1:
            self.fields.pop('retrive_url')
        
        elif only_fields:
            for field_name in list(self.fields.keys()):
                if field_name not in only_fields:
                    self.fields.pop(field_name)

    
    def get_author(self, obj):
        author_obj = obj.author

        if not author_obj:
            return None
        
        return AuthorsSerializer(author_obj, only_fields=['name', 'surname', 'retrive_url'], context=self.context).data
    

    def get_category(self, obj):
        category_obj = obj.category.all()

        if not category_obj:
            return None
        
        return [category.name for category in category_obj]


    def get_museum(self, obj):
        museum_obj = obj.museum

        if not museum_obj:
            return None
        
        return MuseumsListSerializer(museum_obj, context=self.context).data


    def get_retrive_url(self, obj):
        request = self.context.get('request')

        if not request:
            return None

        return reverse('exhibits-detail', kwargs={'pk': obj.pk}, request=request)