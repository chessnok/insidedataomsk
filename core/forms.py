from django import forms


def validate_file_extension(valid_extensions=None):
    if valid_extensions is None:
        valid_extensions = ['.csv']

    def validator(value):
        import os
        from django.core.exceptions import ValidationError

        ext = os.path.splitext(value.name)[-1]
        if not ext.lower() in valid_extensions:
            raise ValidationError(
                'Unsupported file extension.')

    return validator


class CalculationForm(forms.Form):
    num_data = forms.FileField(required=True, allow_empty_file=False,
                               validators=[validate_file_extension()])
    image = forms.ImageField(required=True, allow_empty_file=False)
