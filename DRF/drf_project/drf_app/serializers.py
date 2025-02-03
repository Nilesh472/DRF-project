from rest_framework import serializers
from .models import Student
class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length = 255)
    roll = serializers.IntegerField()



    class Meta:
        fields = "__all__"

    def create(self, validated_data):
        inst = Student.objects.create(**validated_data)
        return inst
    
    def update (self, instance, validated_data):
        print(instance.name)
        instance.name = validated_data.get('name', instance.name)
        print(instance.name)
        instance.roll = validated_data.get('roll', instance.roll)
        instance.save()
        return instance
    

    #Field level Validation
    def validate_roll(self, value):
        if value >=200:
            raise serializers.ValidationError('seat full')
        return value
    
    # object level validation
    def validate(self, data):
        name = data.get('name')
        if len(name) <= 1:
            raise serializers.ValidationError('name is too short')
        return data

