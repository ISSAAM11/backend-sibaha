from rest_framework import serializers
from .models import Academy, Course, CourseTiming, Invitation, OpeningHour, SwimmingPool


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


class CourseTimingSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format='%H:%M')
    end_time   = serializers.TimeField(format='%H:%M')

    class Meta:
        model  = CourseTiming
        fields = ['id', 'weekday', 'start_time', 'end_time']


class CourseSerializer(serializers.ModelSerializer):
    timings    = CourseTimingSerializer(many=True, read_only=True)
    coach_id   = serializers.IntegerField(source='coach.id', read_only=True, allow_null=True)
    coach_name = serializers.CharField(source='coach.username', read_only=True, allow_null=True)
    pool_id    = serializers.IntegerField(source='pool.id', read_only=True, allow_null=True)

    class Meta:
        model  = Course
        fields = [
            'id', 'name', 'description', 'level',
            'academy', 'coach_id', 'coach_name', 'pool_id',
            'timings', 'created_at',
        ]


class InvitationSerializer(serializers.ModelSerializer):
    from_owner_name = serializers.CharField(source='from_owner.username', read_only=True)
    to_coach_name   = serializers.CharField(source='to_coach.username', read_only=True)
    course_name     = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model  = Invitation
        fields = [
            'id', 'from_owner', 'from_owner_name',
            'to_coach', 'to_coach_name',
            'course', 'course_name',
            'status', 'created_at', 'responded_at',
        ]
        read_only_fields = ['status', 'created_at', 'responded_at']


class AcademyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Academy
        fields = ['name', 'city', 'address', 'description', 'specialities', 'picture', 'latitude', 'longitude']


class AcademyListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='picture', use_url=True, allow_null=True)

    class Meta:
        model  = Academy
        fields = ['id', 'name', 'city', 'address', 'specialities', 'latitude', 'longitude', 'image', 'created_at', 'updated_at']


class AcademySerializer(serializers.ModelSerializer):
    image                  = serializers.ImageField(source='picture', use_url=True, allow_null=True)
    pool_list              = serializers.SerializerMethodField()
    weekday_availabilities = OpeningHourSerializer(source='opening_hours', many=True)
    courses                = CourseSerializer(many=True, read_only=True)
    owner_id               = serializers.IntegerField(source='owner.id', read_only=True, allow_null=True)

    class Meta:
        model  = Academy
        fields = [
            'id', 'name', 'owner_id', 'city', 'address', 'description',
            'latitude', 'longitude',
            'specialities', 'image', 'pool_list', 'courses',
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
