from rest_framework import serializers
from .models import User, Profile, Plants, Tips, Gallery, Diary
from rest_framework.reverse import reverse


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)


class UserRegistration(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]

    def create(self, validated_data):

        user = User.objects.create(
            username = validated_data.get('username')
        )

        user.set_password(validated_data.get('password'))
        user.is_active = False
        user.save()

        Profile.objects.create(
            user = user,
            token = None
        )

        return user


class TipsSerializer(serializers.ModelSerializer):
    retrive_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tips
        fields = [
            'id',
            'retrive_url',
            'plant',
            'tip'
        ]
    
    def get_retrive_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse('admin-tips-detail', kwargs={'pk': obj.pk}, request=request)


class TipsPlantShownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tips
        fields = [
            'tip'
        ]


class PlantsSerializer(serializers.ModelSerializer):
    
    username = serializers.SerializerMethodField(read_only=True)
    tips = serializers.SerializerMethodField(read_only=True)
    retrive_url = serializers.SerializerMethodField(read_only=True)
    notes = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = Plants
        fields = [
            'id',
            'plant',
            'retrive_url',
            'username',
            'description',
            'lightning',
            'fertilizers',
            'watering_periods_days',
            'last_watering_date',
            'create_date',
            'tips',
            'notes'
        ]


    def create(self, validated_data):
        profile = validated_data.pop('profile')
        plant = Plants.objects.create(profile=profile, **validated_data)
        
        return plant
    

    def get_username(self, obj):
        if not obj or not hasattr(obj, 'profile'):
            return None

        user = User.objects.get(pk=obj.profile.user_id)
        return user.username
    

    def get_tips(self, obj):
        if not obj:
            return None
        
        return Tips.objects.filter(plant=obj).count()
    

    def get_notes(self, obj):
        if not obj:
            return None
        
        return Diary.objects.filter(plant=obj).count()


    def get_retrive_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse('retrive-plant', kwargs={'pk': obj.pk}, request=request)


class PlantRetriveSerializator(PlantsSerializer):

    plant_gallery = serializers.SerializerMethodField(read_only=True)
    
    class Meta(PlantsSerializer.Meta):
        fields = [field for field in PlantsSerializer.Meta.fields if field != 'retrive_url'] + [
            'plant_gallery'
        ]

        # fields = PlantsSerializer.Meta.fields + [
        #     'plant_gallery'
        # ]
    
    def get_plant_gallery(self, obj):
        if not obj:
            return None
        
        gallery = Gallery.objects.filter(plant=obj).all()

        return GallerySerializer(gallery, many=True).data
    

    def get_notes(self, obj):
        if not obj:
            return None
        
        notes = Diary.objects.filter(plant=obj).all()
        return DiarySerializer(notes, many=True).data
    

    def get_tips(self, obj):
        if not obj:
            return None
        
        tips = Tips.objects.filter(plant=obj).all()
        return TipsPlantShownSerializer(tips, many=True).data


class GallerySerializer(serializers.ModelSerializer):
    plant = serializers.PrimaryKeyRelatedField(queryset=Plants.objects.none())

    class Meta:
        model = Gallery
        fields = [
            'plant',
            'image',
            'state',
            'date'
        ]

    def __init__(self, *args, **kwargs):
        super(GallerySerializer, self).__init__(*args, **kwargs)  
        request = self.context.get('request')

        if request:
            profile = Profile.objects.get(user=request.user)
            self.fields['plant'].queryset = Plants.objects.filter(profile=profile) 


class DiarySerializer(serializers.ModelSerializer):
    retrive_url = serializers.SerializerMethodField(read_only=True)
    plant = serializers.PrimaryKeyRelatedField(queryset=Plants.objects.none())
    
    class Meta:
        model = Diary
        fields = [
            'id',
            'retrive_url',
            'plant',
            'note'
        ]
    
    def __init__(self, *args, **kwargs):
        super(DiarySerializer, self).__init__(*args, **kwargs)  
        request = self.context.get('request')

        if request:
            profile = Profile.objects.get(user=request.user)
            self.fields['plant'].queryset = Plants.objects.filter(profile=profile) 

    
    def create(self, validated_data):
        profile = validated_data.pop('profile')
        dairy = Diary.objects.create(profile=profile, **validated_data)

        return dairy
    

    def get_retrive_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse('diary-detail', kwargs={'pk': obj.pk}, request=request)