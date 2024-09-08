from uuid import uuid4

from django.db import models


def get_upload_path(instance, filename):
    uuid = uuid4().hex
    return f'predictions/{uuid}.{filename.split(".")[-1]}'


class Prediction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('complete', 'Завершено')
    ]

    image = models.ImageField(upload_to=get_upload_path)
    user_result = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    model_result = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    rgb_image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    temperature = models.FloatField()
    humidity = models.FloatField()
    precipitation = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Предсказание'
        verbose_name_plural = 'Предсказания'