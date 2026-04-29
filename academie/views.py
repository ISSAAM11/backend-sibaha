from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Academy, SwimmingPool
from .serializers import AcademyListSerializer, AcademySerializer, SwimmingPoolSerializer


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
