from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from django.utils import timezone

from .models import Academy, Course, Invitation, Review, Subscription, SwimmingPool
from .serializers import (
    AcademyClientSerializer, AcademyCreateSerializer, AcademyListSerializer, AcademySerializer,
    CoachCourseSerializer, InvitationSerializer, ReviewSerializer,
    SubscriptionSerializer,
    SwimmingPoolCreateSerializer, SwimmingPoolSerializer,
)


class AcademyListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        academies = Academy.objects.all()
        serializer = AcademyListSerializer(academies, many=True, context={'request': request})
        return Response({'data': serializer.data})


class AcademyDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            academy = Academy.objects.prefetch_related('swimming_pools', 'opening_hours').get(pk=pk)
        except Academy.DoesNotExist:
            return Response({'error': 'Academy not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AcademySerializer(academy, context={'request': request})
        return Response({'data': serializer.data})


class MyAcademyListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        academies = Academy.objects.filter(owner=request.user).prefetch_related('swimming_pools')
        serializer = AcademyListSerializer(academies, many=True, context={'request': request})
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = AcademyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            out = AcademyListSerializer(serializer.instance, context={'request': request})
            return Response({'data': out.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PoolListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        pools = SwimmingPool.objects.select_related('academy').all()
        serializer = SwimmingPoolSerializer(pools, many=True, context={'request': request})
        return Response({'data': serializer.data})


class PoolDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            pool = SwimmingPool.objects.select_related('academy').get(pk=pk)
        except SwimmingPool.DoesNotExist:
            return Response({'error': 'Pool not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SwimmingPoolSerializer(pool, context={'request': request})
        return Response({'data': serializer.data})


class MyAcademyUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        return self.patch(request, pk)

    def patch(self, request, pk):
        try:
            academy = Academy.objects.prefetch_related('swimming_pools').get(pk=pk, owner=request.user)
        except Academy.DoesNotExist:
            return Response({'error': 'Academy not found or you do not have permission to edit it'},
                          status=status.HTTP_404_NOT_FOUND)

        serializer = AcademyCreateSerializer(academy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_academy = AcademyListSerializer(academy, context={'request': request})
            return Response({'data': updated_academy.data}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MyAcademyPoolCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            academy = Academy.objects.get(pk=pk, owner=request.user)
        except Academy.DoesNotExist:
            return Response({'error': 'Academy not found or permission denied'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = SwimmingPoolCreateSerializer(data=request.data)
        if serializer.is_valid():
            pool = serializer.save(academy=academy)
            out = SwimmingPoolSerializer(pool, context={'request': request})
            return Response({'data': out.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MyAcademyPoolDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_pool(self, pk, pool_pk, user):
        try:
            academy = Academy.objects.get(pk=pk, owner=user)
        except Academy.DoesNotExist:
            return None
        try:
            return academy.swimming_pools.get(pk=pool_pk)
        except SwimmingPool.DoesNotExist:
            return None

    def patch(self, request, pk, pool_pk):
        pool = self._get_pool(pk, pool_pk, request.user)
        if pool is None:
            return Response({'error': 'Pool not found or permission denied'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = SwimmingPoolCreateSerializer(pool, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            out = SwimmingPoolSerializer(pool, context={'request': request})
            return Response({'data': out.data})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, pool_pk):
        pool = self._get_pool(pk, pool_pk, request.user)
        if pool is None:
            return Response({'error': 'Pool not found or permission denied'},
                            status=status.HTTP_404_NOT_FOUND)
        pool.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcademyInvitationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_owned_academy(self, pk, user):
        try:
            return Academy.objects.get(pk=pk, owner=user)
        except Academy.DoesNotExist:
            raise PermissionDenied('You do not own this academy.')

    def get(self, request, pk):
        self._get_owned_academy(pk, request.user)
        invitations = Invitation.objects.filter(
            academy_id=pk, from_owner=request.user
        ).select_related('to_coach', 'from_owner', 'course')
        serializer = InvitationSerializer(invitations, many=True, context={'request': request})
        return Response({'data': serializer.data})

    def post(self, request, pk):
        academy = self._get_owned_academy(pk, request.user)
        serializer = InvitationSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(from_owner=request.user, academy=academy)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)


class AcademyReviewListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, pk):
        if not Academy.objects.filter(pk=pk).exists():
            return Response({'error': 'Academy not found'}, status=status.HTTP_404_NOT_FOUND)
        reviews = Review.objects.filter(academy_id=pk).select_related('user')
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response({'data': serializer.data})

    def post(self, request, pk):
        try:
            academy = Academy.objects.get(pk=pk)
        except Academy.DoesNotExist:
            return Response({'error': 'Academy not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        review, created = Review.objects.get_or_create(
            academy=academy,
            user=request.user,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data.get('comment', ''),
            },
        )
        if not created:
            review.rating = serializer.validated_data['rating']
            review.comment = serializer.validated_data.get('comment', '')
            review.save()

        out = ReviewSerializer(review, context={'request': request})
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({'data': out.data}, status=http_status)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.user_type != 'user':
            return Response({'error': 'Only regular users can subscribe to academies.'},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            academy = Academy.objects.get(pk=pk)
        except Academy.DoesNotExist:
            return Response({'error': 'Academy not found'}, status=status.HTTP_404_NOT_FOUND)

        if Subscription.objects.filter(user=request.user, academy=academy).exists():
            return Response({'error': 'You are already subscribed to this academy.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription = Subscription.objects.create(
            user=request.user,
            academy=academy,
            price_at_subscription=academy.monthly_price,
        )
        out = SubscriptionSerializer(subscription)
        return Response({'data': out.data}, status=status.HTTP_201_CREATED)


class MySubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user).select_related('academy')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response({'data': serializer.data})


class AcademyClientListView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_owned_academy(self, pk, user):
        try:
            return Academy.objects.get(pk=pk, owner=user)
        except Academy.DoesNotExist:
            raise PermissionDenied('You do not own this academy.')

    def get(self, request, pk):
        self._get_owned_academy(pk, request.user)
        subscriptions = (
            Subscription.objects
            .filter(academy_id=pk)
            .select_related('user')
        )
        serializer = AcademyClientSerializer(subscriptions, many=True, context={'request': request})
        return Response({'data': serializer.data})


class AcademyClientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_subscription(self, academy_pk, subscription_pk, owner):
        try:
            Academy.objects.get(pk=academy_pk, owner=owner)
        except Academy.DoesNotExist:
            raise PermissionDenied('You do not own this academy.')
        try:
            return Subscription.objects.get(pk=subscription_pk, academy_id=academy_pk)
        except Subscription.DoesNotExist:
            return None

    def delete(self, request, pk, subscription_pk):
        subscription = self._get_subscription(pk, subscription_pk, request.user)
        if subscription is None:
            return Response({'error': 'Client subscription not found'}, status=status.HTTP_404_NOT_FOUND)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyInvitationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'coach':
            return Response({'error': 'Only coaches can access their invitations.'},
                            status=status.HTTP_403_FORBIDDEN)
        invitations = (
            Invitation.objects
            .filter(to_coach=request.user)
            .select_related('from_owner', 'to_coach', 'academy', 'course')
        )
        serializer = InvitationSerializer(invitations, many=True, context={'request': request})
        return Response({'data': serializer.data})


class MyInvitationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.user_type != 'coach':
            return Response({'error': 'Only coaches can respond to invitations.'},
                            status=status.HTTP_403_FORBIDDEN)
        try:
            invitation = Invitation.objects.select_related('from_owner', 'to_coach', 'academy', 'course').get(
                pk=pk, to_coach=request.user
            )
        except Invitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ('accepted', 'declined'):
            return Response({'error': "Status must be 'accepted' or 'declined'."},
                            status=status.HTTP_400_BAD_REQUEST)

        if invitation.status != 'pending':
            return Response({'error': 'This invitation has already been responded to.'},
                            status=status.HTTP_400_BAD_REQUEST)

        invitation.status = new_status
        invitation.responded_at = timezone.now()
        invitation.save()

        serializer = InvitationSerializer(invitation, context={'request': request})
        return Response({'data': serializer.data})


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'coach':
            return Response({'error': 'Only coaches can access their courses.'},
                            status=status.HTTP_403_FORBIDDEN)
        courses = (
            Course.objects
            .filter(coach=request.user)
            .select_related('academy', 'pool')
            .prefetch_related('timings')
        )
        serializer = CoachCourseSerializer(courses, many=True, context={'request': request})
        return Response({'data': serializer.data})
