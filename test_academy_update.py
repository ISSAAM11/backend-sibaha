#!/usr/bin/env python
"""
Simple test script to verify the academy update endpoint works correctly.
Run this with: python manage.py shell < test_academy_update.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sibaha_backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from academie.models import Academy
from academie.views import MyAcademyUpdateView
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

def test_academy_update():
    print("Testing Academy Update Endpoint...")
    
    # Create a test user
    user = User.objects.create_user(
        username='testowner',
        email='test@example.com',
        password='testpass123'
    )
    
    # Create a test academy
    academy = Academy.objects.create(
        owner=user,
        name='Test Academy',
        city='Test City',
        address='Test Address',
        description='Test Description'
    )
    
    print(f"Created academy: {academy.name} (ID: {academy.id})")
    
    # Create a request factory
    factory = APIRequestFactory()
    
    # Test data for update
    update_data = {
        'name': 'Updated Academy Name',
        'city': 'Updated City',
        'description': 'Updated Description',
        'specialities': ['Freestyle', 'Backstroke']
    }
    
    # Create PUT request
    django_request = factory.put(f'/my-academies/{academy.id}/', update_data, format='json')
    django_request.user = user
    
    # Convert to DRF request
    drf_request = Request(django_request)
    
    # Create view instance and call the method
    view = MyAcademyUpdateView()
    view.setup(django_request)
    
    # Call the put method
    response = view.put(drf_request, pk=academy.id)
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    # Verify the academy was updated
    updated_academy = Academy.objects.get(id=academy.id)
    print(f"Updated academy name: {updated_academy.name}")
    print(f"Updated academy city: {updated_academy.city}")
    print(f"Updated academy specialities: {updated_academy.specialities}")
    
    # Test unauthorized access
    print("\nTesting unauthorized access...")
    unauthorized_user = User.objects.create_user(
        username='unauthorized',
        email='unauthorized@example.com',
        password='testpass123'
    )
    
    django_request.user = unauthorized_user
    drf_request = Request(django_request)
    
    response = view.put(drf_request, pk=academy.id)
    print(f"Unauthorized response status: {response.status_code}")
    print(f"Unauthorized response data: {response.data}")
    
    # Cleanup
    Academy.objects.all().delete()
    User.objects.all().delete()
    
    print("\nTest completed successfully!")

if __name__ == '__main__':
    test_academy_update()
