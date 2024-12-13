from django.shortcuts import render, HttpResponse
from .models import Student
from .serializers import StudentSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io
from django.views.decorators.csrf import csrf_exempt
#single student data 
def student_detail(request):
    stu = Student.objects.get(id = 1)
    stu_ser = StudentSerializer(stu)
    json_data = JSONRenderer().render(stu_ser.data)
    return HttpResponse(json_data, content_type = 'application/json')

#CRUD operation on complete dataset
@csrf_exempt
def students_detail_list(request):
    if request.method == "GET":
        stu = Student.objects.all()
        stu_ser = StudentSerializer(stu, many = True)
        json_data = JSONRenderer().render(stu_ser.data)
        return HttpResponse(json_data, content_type = 'application/json')
    
    if request.method == "POST":
        json_data = request.body
        stream = io.BytesIO(json_data)
        pythondata = JSONParser().parse(stream)
        serializer = StudentSerializer(data = pythondata)

        if serializer.is_valid():
            serializer.save()
            json_data = JSONRenderer().render(serializer.data)
        else:
            json_data = JSONRenderer().render(serializer.errors)

        return HttpResponse(json_data, content_type = 'application/json')
    
    if request.method == "PUT":
        json_data = request.body
        stream = io.BytesIO(json_data)
        pythondata = JSONParser().parse(stream)
        id = pythondata.get('id')
        stu = Student.objects.get(id=id)
        serializer = StudentSerializer(stu, data=pythondata, partial=True)
        if serializer.is_valid():
            serializer.save()
            json_data = JSONRenderer().render(serializer.data)
        else:
            json_data = JSONRenderer().render(serializer.errors)
        return HttpResponse(json_data, content_type='application/json')

    if request.method == "DELETE":
        json_data = request.body
        stream = io.BytesIO(json_data)
        pythondata = JSONParser().parse(stream)
        id = pythondata.get('id')
        stu = Student.objects.get(id=id)
        stu.delete()
        return HttpResponse({'msg': 'Data deleted'}, content_type='application/json')
    