from rest_framework import serializers

from .models import Creation


class CreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creation
        fields = ('name', 'code', 'svg', 'is_animated')


class CreationOutputSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url')
    user = serializers.SlugField(source='author.username')

    class Meta:
        model = Creation
        fields = ('slug', 'url', 'name', 'user')


class LoveSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    author = serializers.SlugField()
    action = serializers.SlugField()

    def validate_action(self, value):
        if value not in ['love', 'unlove']:
            raise serializers.ValidationError("Allowed actions: love, unlove")
        return value
