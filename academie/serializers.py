from rest_framework import serializers
from .models import Academy, OpeningHour, SwimmingPool


class OpeningHourSerializer(serializers.ModelSerializer):
    weekday    = serializers.CharField(source='day')
    start_time = serializers.TimeField(source='opening_time', format='%H:%M', allow_null=True)
    end_time   = serializers.TimeField(source='closing_time', format='%H:%M', allow_null=True)

    class Meta:
        model  = OpeningHour
        fields = ['weekday', 'start_time', 'end_time', 'is_closed']


class SwimmingPoolSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, allow_null=True)
    academy_name = serializers.CharField(source='academy.name', read_only=True)
    academy_id = serializers.IntegerField(source='academy.id', read_only=True)

    class Meta:
        model = SwimmingPool
        fields = [
            'id', 'name', 'academy_name', 'academy_id',
            'speciality', 'dimension', 'heated', 'showers',
            'image', 'created_at',
        ]


class AcademyListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='picture', use_url=True, allow_null=True)

    class Meta:
        model  = Academy
        fields = ['id', 'name', 'city', 'address', 'specialities', 'image', 'created_at', 'updated_at']


class AcademySerializer(serializers.ModelSerializer):
    image                  = serializers.ImageField(source='picture', use_url=True, allow_null=True)
    pool_list              = serializers.SerializerMethodField()
    weekday_availabilities = OpeningHourSerializer(source='opening_hours', many=True)

    class Meta:
        model  = Academy
        fields = [
            'id', 'name', 'city', 'address', 'description',
            'specialities', 'image', 'pool_list',
            'weekday_availabilities', 'created_at', 'updated_at',
        ]

    def get_pool_list(self, obj):
        request = self.context.get('request')
        return [
            {
                'id': p.id,
                'name': p.name,
                'image': request.build_absolute_uri(p.image.url) if request and p.image else None,
            }
            for p in obj.swimming_pools.all()
        ]
