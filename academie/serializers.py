from rest_framework import serializers
from .models import Academy, OpeningHour, SwimmingPool


class OpeningHourSerializer(serializers.ModelSerializer):
    weekday    = serializers.CharField(source='day')
    start_time = serializers.TimeField(source='opening_time', format='%H:%M', allow_null=True)
    end_time   = serializers.TimeField(source='closing_time', format='%H:%M', allow_null=True)

    class Meta:
        model  = OpeningHour
        fields = ['weekday', 'start_time', 'end_time', 'is_closed']


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
        return list(obj.swimming_pools.values_list('name', flat=True))
