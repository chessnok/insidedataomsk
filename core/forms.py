from django import forms
from .models import Prediction


def validate_file_extension(valid_extensions=None):
    if valid_extensions is None:
        valid_extensions = ['.tif', '.tiff']

    def validator(value):
        import os
        from django.core.exceptions import ValidationError

        ext = os.path.splitext(value.name)[-1]
        if not ext.lower() in valid_extensions:
            raise ValidationError(
                'Unsupported file extension. Allowed: .tif, .tiff')

    return validator


class CalculationForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['image', 'temperature', 'humidity', 'precipitation',
                  'wind_speed', 'wind_direction']

    image = forms.FileField(required=True, allow_empty_file=False,
                            validators=[validate_file_extension()])
    temperature = forms.FloatField(required=True, label="Температура")
    humidity = forms.FloatField(required=True, label="Влажность", min_value=0,
                                max_value=100)
    precipitation = forms.FloatField(required=True, label="Осадки")
    wind_speed = forms.FloatField(required=True, label="Скорость ветра")
    wind_direction = forms.IntegerField(required=True,
                                        label="Направление ветра")
