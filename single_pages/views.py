from django.shortcuts import render


def twister(request):
    return render(request, 'twister.html')
