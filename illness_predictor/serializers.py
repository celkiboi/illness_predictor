from rest_framework import serializers
from .models import IllnessPrediction

class IllnessPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IllnessPrediction
        fields = '__all__'
