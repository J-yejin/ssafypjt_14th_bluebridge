from django.shortcuts import render

# Create your views here.
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from policies.models import Policy
from policies.serializers import PolicySerializer

@api_view(["GET"])
def policy_list(request):
    qs = Policy.objects.all()
    total = qs.count()

    if total <= 20:
        policies = qs
    else:
        random_ids = random.sample(
            list(qs.values_list("id", flat=True)),
            20
        )
        policies = qs.filter(id__in=random_ids)

    serializer = PolicySerializer(policies, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def policy_detail(request, id):
    try:
        policy = Policy.objects.get(id=id)
    except Policy.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    serializer = PolicySerializer(policy)
    return Response(serializer.data)
