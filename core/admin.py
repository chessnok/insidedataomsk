from django.contrib import admin

from core.models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['id']
    readonly_fields = ['id', 'created_at']
    fields = ['id', 'image', 'user_result', 'model_result', 'temperature',
              'humidity', 'precipitation', 'wind_speed', 'wind_direction',
              'status', 'created_at']
    ordering = ['-created_at']
