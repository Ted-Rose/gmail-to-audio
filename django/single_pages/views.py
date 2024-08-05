from django.shortcuts import render

# Create your views here.
def twister(request):
    return render(request, 'twister.html')