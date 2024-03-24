import flet as ft

from components.weather_widget import Weather
from components.weather_widget import WeatherAsync


def main(page: ft.Page):
    """

    :param page: ft.Page:
    :param page: ft.Page:

    """

    weather_widget = Weather()
    weather_widget_async = WeatherAsync()

    page.add(weather_widget)
    page.add(weather_widget_async)


ft.app(main)
