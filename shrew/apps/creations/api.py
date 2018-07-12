from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import CreationSerializer, CreationOutputSerializer
from .models import Creation


class CreationApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        creation = None
        base = None
        if request.data.get('slug'):
            creation = get_object_or_404(Creation, slug=request.data['slug'])
            if creation.author != request.user:
                base = creation
                creation = None

        if creation:
            creation_serializer = CreationSerializer(creation, data=request.data)
        else:
            creation_serializer = CreationSerializer(data=request.data)

        creation_serializer.is_valid(raise_exception=True)
        creation = creation_serializer.save(author=request.user, base=base)

        creation_output = CreationOutputSerializer(creation)

        return Response(creation_output.data)
