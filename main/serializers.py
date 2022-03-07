from rest_framework import serializers
from .models import Staff, Attendance


class MainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class AttendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
