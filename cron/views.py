from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from . import zeus

@api_view(['GET'])
def runjob(request):
    return Response(zeus.updateFive9Files(), status=status.HTTP_200_OK)