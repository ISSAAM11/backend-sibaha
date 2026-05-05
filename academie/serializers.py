from django.db.models import Avg, Count
from rest_framework import serializers

from .models import Academy, Course, CourseTiming, Invitation, OpeningHour, Review, Subscription, SwimmingPool


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
    timings       = CourseTimingSerializer(many=True, read_only=True)
    coach_id      = serializers.IntegerField(source='coach.id', read_only=True, allow_null=True)
    coach_name    = serializers.CharField(source='coach.username', read_only=True, allow_null=True)
    coach_picture = serializers.SerializerMethodField(read_only=True)
    pool_id       = serializers.IntegerField(source='pool.id', read_only=True, allow_null=True)

    def get_coach_picture(self, obj):
        request = self.context.get('request')
        if obj.coach and obj.coach.picture and request:
            return request.build_absolute_uri(obj.coach.picture.url)
        return None

    class Meta:
        model  = Course
        fields = [
            'id', 'name', 'description', 'level', 'price_per_month',
            'academy', 'coach_id', 'coach_name', 'coach_picture', 'pool_id',
            'timings', 'created_at',
        ]


class CourseTimingWriteSerializer(serializers.Serializer):
    weekday    = serializers.ChoiceField(choices=[c[0] for c in CourseTiming._meta.get_field('weekday').choices])
    start_time = serializers.TimeField()
    end_time   = serializers.TimeField()


class CourseWriteSerializer(serializers.ModelSerializer):
    timings = CourseTimingWriteSerializer(many=True, required=False, default=list)
    coach   = serializers.PrimaryKeyRelatedField(
        queryset=Course._meta.get_field('coach').related_model.objects.filter(user_type='coach'),
        allow_null=True, required=False,
    )
    pool    = serializers.PrimaryKeyRelatedField(
        queryset=SwimmingPool.objects.all(),
        allow_null=True, required=False,
    )

    class Meta:
        model  = Course
        fields = ['name', 'description', 'level', 'price_per_month', 'coach', 'pool', 'timings']

    def create(self, validated_data):
        timings_data = validated_data.pop('timings', [])
        course = Course.objects.create(**validated_data)
        CourseTiming.objects.bulk_create([
            CourseTiming(course=course, **t) for t in timings_data
        ])
        return course

    def update(self, instance, validated_data):
        timings_data = validated_data.pop('timings', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if timings_data is not None:
            instance.timings.all().delete()
            CourseTiming.objects.bulk_create([
                CourseTiming(course=instance, **t) for t in timings_data
            ])
        return instance


class InvitationSerializer(serializers.ModelSerializer):
    from_owner_name  = serializers.CharField(source='from_owner.username', read_only=True)
    to_coach_name    = serializers.CharField(source='to_coach.username', read_only=True)
    to_coach_picture = serializers.SerializerMethodField(read_only=True)
    course_name      = serializers.SerializerMethodField(read_only=True)
    academy_id       = serializers.SerializerMethodField(read_only=True)
    academy_name     = serializers.SerializerMethodField(read_only=True)

    def get_to_coach_picture(self, obj):
        request = self.context.get('request')
        if obj.to_coach.picture and request:
            return request.build_absolute_uri(obj.to_coach.picture.url)
        return None

    def get_course_name(self, obj):
        return obj.course.name if obj.course else None

    def get_academy_id(self, obj):
        return obj.academy.id if obj.academy else None

    def get_academy_name(self, obj):
        return obj.academy.name if obj.academy else None

    class Meta:
        model  = Invitation
        fields = [
            'id', 'from_owner', 'from_owner_name',
            'to_coach', 'to_coach_name', 'to_coach_picture',
            'academy_id', 'academy_name',
            'course', 'course_name',
            'status', 'created_at', 'responded_at',
        ]
        read_only_fields = ['from_owner', 'status', 'created_at', 'responded_at']


class ReviewSerializer(serializers.ModelSerializer):
    username     = serializers.CharField(source='user.username', read_only=True)
    user_picture = serializers.SerializerMethodField()

    class Meta:
        model  = Review
        fields = ['id', 'user_id', 'username', 'user_picture', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user_id', 'username', 'user_picture', 'created_at']

    def get_user_picture(self, obj):
        request = self.context.get('request')
        if obj.user.picture and request:
            return request.build_absolute_uri(obj.user.picture.url)
        return None


class SwimmingPoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SwimmingPool
        fields = ['name', 'speciality', 'dimension', 'heated', 'showers', 'image']


class AcademyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Academy
        fields = ['name', 'city', 'address', 'description', 'specialities', 'picture', 'latitude', 'longitude']


class AcademyListSerializer(serializers.ModelSerializer):
    image          = serializers.ImageField(source='picture', use_url=True, allow_null=True)
    pool_list      = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count   = serializers.SerializerMethodField()
    coaches_count  = serializers.SerializerMethodField()
    clients_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Academy
        fields = [
            'id', 'name', 'city', 'address', 'description', 'specialities',
            'latitude', 'longitude', 'image', 'pool_list',
            'monthly_price', 'average_rating', 'review_count',
            'coaches_count', 'clients_count',
            'created_at', 'updated_at',
        ]

    def get_pool_list(self, obj):
        request = self.context.get('request')
        return [
            {
                'id': p.id,
                'name': p.name,
                'image': request.build_absolute_uri(p.image.url) if request and p.image else None,
                'speciality': p.speciality,
                'dimension': p.dimension,
                'heated': p.heated,
                'showers': p.showers,
            }
            for p in obj.swimming_pools.all()
        ]

    def get_average_rating(self, obj):
        result = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result is not None else None

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_coaches_count(self, obj):
        return obj.coach_invitations.filter(status='accepted').count()

    def get_clients_count(self, obj):
        return obj.subscriptions.count()


class AcademySerializer(serializers.ModelSerializer):
    image                  = serializers.ImageField(source='picture', use_url=True, allow_null=True)
    pool_list              = serializers.SerializerMethodField()
    weekday_availabilities = OpeningHourSerializer(source='opening_hours', many=True)
    courses                = CourseSerializer(many=True, read_only=True)
    owner_id               = serializers.IntegerField(source='owner.id', read_only=True, allow_null=True)
    average_rating         = serializers.SerializerMethodField()
    review_count           = serializers.SerializerMethodField()
    coaches_count          = serializers.SerializerMethodField()
    clients_count          = serializers.SerializerMethodField()

    class Meta:
        model  = Academy
        fields = [
            'id', 'name', 'owner_id', 'city', 'address', 'description',
            'latitude', 'longitude',
            'specialities', 'image', 'pool_list', 'courses',
            'weekday_availabilities',
            'monthly_price', 'average_rating', 'review_count',
            'coaches_count', 'clients_count',
            'created_at', 'updated_at',
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

    def get_average_rating(self, obj):
        result = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result is not None else None

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_coaches_count(self, obj):
        return obj.coach_invitations.filter(status='accepted').count()

    def get_clients_count(self, obj):
        return obj.subscriptions.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    academy_name    = serializers.CharField(source='academy.name', read_only=True)
    academy_city    = serializers.CharField(source='academy.city', read_only=True)
    academy_address = serializers.CharField(source='academy.address', read_only=True)
    course_id       = serializers.IntegerField(source='course.id', read_only=True, allow_null=True)
    course_name     = serializers.CharField(source='course.name', read_only=True, allow_null=True)
    course_level    = serializers.CharField(source='course.level', read_only=True, allow_null=True)
    coach_name      = serializers.SerializerMethodField()
    timings         = serializers.SerializerMethodField()

    def get_coach_name(self, obj):
        if obj.course and obj.course.coach:
            coach = obj.course.coach
            full_name = f"{coach.first_name} {coach.last_name}".strip()
            return full_name or coach.username
        return None

    def get_timings(self, obj):
        if obj.course:
            return CourseTimingSerializer(obj.course.timings.all(), many=True).data
        return []

    class Meta:
        model  = Subscription
        fields = [
            'id', 'academy_id', 'academy_name', 'academy_city', 'academy_address',
            'course_id', 'course_name', 'course_level', 'coach_name', 'timings',
            'price_at_subscription', 'status', 'subscribed_at',
        ]
        read_only_fields = fields


class AcademyClientSerializer(serializers.ModelSerializer):
    user_id      = serializers.IntegerField(source='user.id', read_only=True)
    username     = serializers.CharField(source='user.username', read_only=True)
    email        = serializers.CharField(source='user.email', read_only=True)
    user_picture = serializers.SerializerMethodField()

    class Meta:
        model  = Subscription
        fields = ['id', 'user_id', 'username', 'email', 'user_picture', 'price_at_subscription', 'status', 'subscribed_at']
        read_only_fields = fields

    def get_user_picture(self, obj):
        request = self.context.get('request')
        if obj.user.picture and request:
            return request.build_absolute_uri(obj.user.picture.url)
        return None


class CoachCourseSerializer(serializers.ModelSerializer):
    timings      = CourseTimingSerializer(many=True, read_only=True)
    academy_id   = serializers.IntegerField(source='academy.id', read_only=True)
    academy_name = serializers.CharField(source='academy.name', read_only=True)
    pool_id      = serializers.SerializerMethodField()
    pool_name    = serializers.SerializerMethodField()

    def get_pool_id(self, obj):
        return obj.pool.id if obj.pool else None

    def get_pool_name(self, obj):
        return obj.pool.name if obj.pool else None

    class Meta:
        model  = Course
        fields = [
            'id', 'name', 'description', 'level',
            'academy_id', 'academy_name',
            'pool_id', 'pool_name',
            'timings', 'created_at',
        ]
