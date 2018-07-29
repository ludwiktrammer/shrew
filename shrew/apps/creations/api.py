from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import CreationSerializer, CreationOutputSerializer, LoveSerializer
from .models import Creation


class CreationApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        creation = None
        base = None
        if request.data.get('slug') and request.data.get('user'):
            creation = get_object_or_404(
                Creation,
                slug=request.data['slug'],
                author__username=request.data['user'],
            )
            if creation.author != request.user:
                base = creation
                creation = None

        if creation:
            creation_serializer = CreationSerializer(creation, data=request.data)
        else:
            creation_serializer = CreationSerializer(data=request.data)

        creation_serializer.is_valid(raise_exception=True)

        if base:
            creation = creation_serializer.save(author=request.user, base=base)
        else:
            creation = creation_serializer.save(author=request.user)

        creation_output = CreationOutputSerializer(creation)

        return Response(creation_output.data)


class LoveApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        creation = get_object_or_404(Creation, slug=data['slug'], author__username=data['author'])
        if data['action'] == 'love':
            creation.loving.add(request.user)
        else:
            creation.loving.remove(request.user)

        return Response({'status': 'ok'})

