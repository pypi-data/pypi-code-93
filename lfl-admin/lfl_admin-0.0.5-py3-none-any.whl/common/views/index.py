from django.shortcuts import render


def Index(request):
    return render(request, 'index.html')


# def IndexHelp(request):
#     return render(request, 'index.html')
