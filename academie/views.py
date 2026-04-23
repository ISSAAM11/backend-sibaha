from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Academy
from .serializers import AcademySerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def academy_list(request):
    academies = Academy.objects.prefetch_related('swimming_pools', 'opening_hours').all()
    serializer = AcademySerializer(academies, many=True, context={'request': request})
    return Response({'data': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def academy_detail(request, pk):
    try:
        academy = Academy.objects.prefetch_related('swimming_pools', 'opening_hours').get(pk=pk)
    except Academy.DoesNotExist:
        return Response({'error': 'Academy not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = AcademySerializer(academy, context={'request': request})
    return Response({'data': serializer.data})
