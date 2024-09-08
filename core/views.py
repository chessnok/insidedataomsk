from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.conf import settings
from io import BytesIO

from .forms import CalculationForm
from .models import Prediction
from .ml import get_mask, draw_wind_arrow, color_mask

def image_to_bytes(image):
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    return image_io.getvalue()
def home(request):
    if request.method == "POST":
        form = CalculationForm(request.POST, request.FILES)
        if form.is_valid():
            prediction = form.save()
            file_path = prediction.image.path
            mask, rgb_image = get_mask(file_path, prediction.humidity, prediction.wind_speed, settings.UNET)
            user_mask = draw_wind_arrow(color_mask(rgb_image, mask), prediction.wind_speed, prediction.wind_direction)
            prediction.rgb_image.save('rgb_image.png', ContentFile(image_to_bytes(rgb_image)))
            prediction.user_result.save('user_mask.png', ContentFile(image_to_bytes(user_mask)))
            prediction.model_result.save('mask.png', ContentFile(image_to_bytes(mask)))
            prediction.status = 'complete'
            prediction.save()
            return redirect('answer', id=prediction.id)
    else:
        form = CalculationForm()

    return render(request, "website/home.html", {"form": form, "predictions": Prediction.objects.filter(status='complete')})

def answer(request, id):
    prediction = get_object_or_404(Prediction, id=id)
    return render(request, 'website/answer.html',
                  {"prediction": prediction})
