from rest_framework import serializers

from .models import Creation


class CreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creation
        fields = ('name', 'code', 'svg', 'is_animated')


class CreationOutputSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url')

    class Meta:
        model = Creation
        fields = ('slug', 'url')
