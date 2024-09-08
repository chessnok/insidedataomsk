# Решение кейса
## Структура решения
- `data/` - Данные и их обработка
  - `data_processing.ipynb` - Jupyter notebook со всем кодом обработки и анализа данных
  - `metadata.csv` - CSV файл с данными о файлах которые мы получили из tiff
  - `jpgs/` - Изображения в формате jpg(первые 3 слоя из tiff)
  - `merged/` - Все tiff файлы  
  - `api.py` - запрос к API для получения данных
- `masks/` - Изображения масок в формате jpg(последний слой из tiff)
- 'insidedataomsk/` - Django проект
- `README.md` - Описание проекта
- `requirements.txt` - Список зависимостей для запуска Django
- `staticfiles/` - Статические файлы
- `templates/` - Шаблонами
- `manage.py` - Файл для управления проектом Django
- `core/` - папка с приложением Django

## Запуск проекта
1. Установить зависимости
```bash pip install -r requirements.txt```
2. Запустить проект
```bash python manage.py runserver```
3. Перейти по адресу http://localhost:8000/
4. Загрузить файлы в форму "Загрузить данные"

## Связаться с нами
- [Telegram](https://t.me/GeorgeWangg)
- [Telegram](https://t.me/mikhailfadin)
