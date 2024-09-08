import math
import rasterio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import segmentation_models_pytorch as smp
from torchvision import transforms
import torch
import tifffile

ML = 0.00025  # коэффициент масштабирования радиометрии
AL = 0.05  # коэффициент смещения радиометрии
K1 = 765.0  # калибровочная константа K1
K2 = 1275.0  # калибровочная константа K2
epsilon = 0.93  # излучательная способность
lambda_ir = 10.9 * 10 ** -6  # длина волны ИК канала (мкм)
rho = 1.438 * 10 ** -2


class TiffData:
    def __init__(self, file_path):
        with rasterio.open(file_path) as tif:
            self.infrared_layer = tif.read(4)  # Инфракрасный канал
            self.green_layer = tif.read(2)  # Зеленый канал
        with tifffile.TiffFile(file_path) as tif:
            image_array = tif.asarray()

        r = image_array[:, :, 0]
        g = image_array[:, :, 1]
        b = image_array[:, :, 2]

        rgb_image = np.stack([r, g, b], axis=-1)

        rgb_image = rgb_image - np.min(rgb_image)
        rgb_image = rgb_image / np.max(rgb_image)
        rgb_image = (rgb_image * 255).astype(np.uint8)
        image_pil = Image.fromarray(rgb_image)
        self.image = image_pil


class UNet:
    def __init__(self):
        self.model = smp.Unet(encoder_name='resnet34',
                              encoder_weights='imagenet',
                              classes=1)
        self.model.eval()

        self.preprocess = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor()
        ])

    def predict(self, image_pil):
        input_image = self.preprocess(image_pil).unsqueeze(0)

        with torch.no_grad():
            output = self.model(input_image)

        mask = (output.squeeze().numpy() > 0.5).astype(np.uint8)
        total_pixels = mask.size
        object_pixels = np.sum(mask)
        percentage_objects = (object_pixels / total_pixels) * 100

        return percentage_objects


def create_mask(green_layer, lst_celsius_normalized, green_border, lst_border):
    condition = (green_layer > green_border) & (
            lst_celsius_normalized > lst_border)
    return np.where(condition, 1, 0)


def calculate_fire_score(percentage_trees, humidity,
                         wind_speed):
    risk = 0
    risk += 0.5 * ((100 - humidity) / 100)
    risk += 0.5 * (wind_speed / 20)
    risk += 0.1 * (percentage_trees / 100)
    return np.clip(risk, 0, 1)


def get_mask(file_path, humidity, wind_speed,
             unet: UNet):
    green_border = 0.05
    lst_border = 0.55
    tiff_data = TiffData(file_path)
    radiance = ML * tiff_data.infrared_layer + AL
    brightness_temp = K2 / (np.log((K1 / radiance) + 1))
    lst = brightness_temp / (1 + (
            lambda_ir * brightness_temp / rho) * np.log(
        epsilon))
    fire_score = calculate_fire_score(unet.predict(tiff_data.image),
                                      humidity, wind_speed)
    lst_normalized = ((lst - lst.min()) / (lst.max() - lst.min())) * (
            1 + fire_score * 0.01)
    mask = create_mask(tiff_data.green_layer, lst_normalized,
                       green_border, lst_border) * 255
    image = Image.fromarray(mask.astype(np.uint8), mode="L")
    return image, tiff_data.image


def color_mask(image, mask, color=(255, 0, 0)):
    image = image.convert("RGB")
    mask = mask.convert("L")
    color_image = Image.new("RGB", image.size, color)
    alpha_mask = mask.point(lambda p: p > 128 and 255)  # Преобразуем белые пиксели в альфа-канал
    result_image = Image.composite(color_image, image, alpha_mask)
    return result_image

def draw_wind_arrow(img, wind_speed, wind_direction, arrow_color=(255, 255, 255), text_size=20):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    center_x, center_y = width // 2, height // 2

    # Длина стрелки
    arrow_length = int(min(width, height) * 0.2)

    # Начальная и конечная точка стрелки
    start_x = center_x - (arrow_length / 2) * math.cos(math.radians(wind_direction))
    start_y = center_y + (arrow_length / 2) * math.sin(math.radians(wind_direction))
    end_x = center_x + (arrow_length / 2) * math.cos(math.radians(wind_direction))
    end_y = center_y - (arrow_length / 2) * math.sin(math.radians(wind_direction))

    # Рисуем линию (тело стрелки)
    draw.line((start_x, start_y, end_x, end_y), fill=arrow_color, width=5)

    # Величина и угол крыльев стрелки
    arrow_head_size = arrow_length * 0.25  # Длина крыльев = 1/4 от длины стрелки
    arrow_head_angle = 30  # Угол между крыльями и основным направлением стрелки

    # Левое крыло
    left_wing_x = end_x - arrow_head_size * math.cos(math.radians(wind_direction + arrow_head_angle))
    left_wing_y = end_y + arrow_head_size * math.sin(math.radians(wind_direction + arrow_head_angle))

    # Правое крыло
    right_wing_x = end_x - arrow_head_size * math.cos(math.radians(wind_direction - arrow_head_angle))
    right_wing_y = end_y + arrow_head_size * math.sin(math.radians(wind_direction - arrow_head_angle))

    # Рисуем крылья стрелки
    draw.polygon([(end_x, end_y), (left_wing_x, left_wing_y), (right_wing_x, right_wing_y)], fill=arrow_color)

    # Рисуем текст (скорость ветра)
    try:
        font = ImageFont.truetype("arial.ttf", text_size)
    except IOError:
        font = ImageFont.load_default()

    text = f"{wind_speed} m/s"
    text_offset = 25  # Смещение текста от конца стрелки
    text_x = end_x + text_offset * math.cos(math.radians(wind_direction))
    text_y = end_y - text_offset * math.sin(math.radians(wind_direction))

    # Отрисовка текста
    draw.text((text_x, text_y), text, fill=arrow_color, font=font)

    return img
