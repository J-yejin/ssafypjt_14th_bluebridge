from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Policy
from .serializers import PolicySerializer


@api_view(['GET'])
def policy_list(request):
    policies = Policy.objects.filter(is_active=True)
    serializer = PolicySerializer(policies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id, is_active=True)
    serializer = PolicySerializer(policy)
    return Response(serializer.data)