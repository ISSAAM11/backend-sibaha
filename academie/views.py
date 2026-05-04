from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Academy, SwimmingPool
from .serializers import AcademyCreateSerializer, AcademyListSerializer, AcademySerializer, SwimmingPoolSerializer


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
        academies = Academy.objects.filter(owner=request.user)
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
            academy = Academy.objects.get(pk=pk, owner=request.user)
        except Academy.DoesNotExist:
            return Response({'error': 'Academy not found or you do not have permission to edit it'},
                          status=status.HTTP_404_NOT_FOUND)

        serializer = AcademyCreateSerializer(academy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_academy = AcademyListSerializer(academy, context={'request': request})
            return Response({'data': updated_academy.data}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
