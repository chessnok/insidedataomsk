from django.http import HttpResponse
from django.shortcuts import render

from core.forms import CalculationForm


def home(request):
    if request.method == "POST":
        form = CalculationForm(request.POST, request.FILES)
        if form.is_valid():
            x_content = request.FILES["num_data"].read()
            y_content = request.FILES["image"].read()
            return HttpResponse(
                "Files processed successfully! Files content: x: {}, y: {}".format(
                    x_content, y_content))
    else:
        form = CalculationForm()

    return render(request, "website/home.html", {"form": form})
