from sklearn.metrics import matthews_corrcoef
import pandas as pd
import numpy as np
from PIL import Image

from core.ml import get_mask, UNet


def calculate_mcc(true_mask, predicted_mask):
    return matthews_corrcoef(true_mask.flatten(), predicted_mask.flatten())


def scale_mcc(mcc):
    return (mcc + 1) / 2


def get_score(path_to_tiffs='data/merged/',
              weather_data_path='weather_data.csv',
              path_to_masks='data/masks/'):
    weather_data = pd.read_csv(weather_data_path, index_col='file_id')
    unet = UNet()
    total_mcc = 0
    for i in range(21):
        img = Image.open(f'{path_to_masks}/{i:02}.jpg').convert(
            'L')
        mask = np.array(img)
        binary_mask = np.where(mask > 128, 1, 0)
        wdata = weather_data.loc[i]
        mask = get_mask(f'{path_to_tiffs}/{i:02}.tiff',
                        wdata['humidity'], wdata['wind_speed'], unet)
        mcc = calculate_mcc(binary_mask, mask)
        scaled_mcc = scale_mcc(mcc)
        total_mcc += scaled_mcc
    return total_mcc / 21


if __name__ == '__main__':
    print(get_score())
