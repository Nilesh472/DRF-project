from django.db import models

# Create your models here.

class Student(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    roll = models.IntegerField()

    def __str__(self):
        return self.name
