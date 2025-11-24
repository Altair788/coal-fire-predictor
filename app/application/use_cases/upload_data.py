import csv
from datetime import datetime, date
from io import TextIOWrapper
from typing import List

from loguru import logger

from app.domain.entities import (
    TemperatureReading,
    FireIncident,
    CoalPile,
    WeatherData,
)
from app.domain.interfaces import (
    TemperatureRepository,
    FireIncidentRepository,
    CoalPileRepository,
    WeatherRepository,
)


class UploadDataService:
    """
    Use Case для загрузки CSV-файлов и сохранения данных в репозитории.
    """

    def __init__(
        self,
        temperature_repo: TemperatureRepository,
        fire_repo: FireIncidentRepository,
        pile_repo: CoalPileRepository,
        weather_repo: WeatherRepository,
    ):
        self.temperature_repo = temperature_repo
        self.fire_repo = fire_repo
        self.pile_repo = pile_repo
        self.weather_repo = weather_repo

    def upload_csv(self, file: TextIOWrapper, data_type: str) -> None:
        """
        Загружает CSV-файл в систему.
        Поддерживаемые типы: 'temperature', 'fires', 'supplies', 'weather'
        """
        if data_type == "temperature":
            self._upload_temperatures(file)
        elif data_type == "fires":
            self._upload_fires(file)
        elif data_type == "supplies":
            self._upload_supplies(file)
        elif data_type == "weather":
            self._upload_weather(file)
        else:
            raise ValueError(f"Неизвестный тип данных: {data_type}")

    def _upload_supplies(self, file: TextIOWrapper) -> None:
        """Загружает данные из supplies.csv"""
        reader = csv.DictReader(file)
        piles = []
        for row_num, row in enumerate(reader, start=1):
            try:
                try:
                    formation_date = datetime.strptime(row["ВыгрузкаНаСклад"], "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(
                        f"Пропущена строка {row_num} в supplies.csv: неверный формат даты "
                        f"'{row.get('ВыгрузкаНаСклад', '<отсутствует>')}'. Ожидается YYYY-MM-DD."
                    )
                    continue

                pile = CoalPile(
                    pile_id=int(row["Штабель"]),
                    coal_type=row["Наим. ЕТСНГ"],
                    formation_date=formation_date,
                    initial_volume_tonnes=float(row["На склад, тн"]),
                    warehouse_id=int(row["Склад"]),
                )
                piles.append(pile)
                logger.debug(f"Загружена запись supplies.csv: pile_id={pile.pile_id}")

            except (ValueError, KeyError) as e:
                logger.error(
                    f"Пропущена строка {row_num} в supplies.csv: ошибка парсинга — {e}. Строка: {row}"
                )
                continue

        if not piles:
            raise ValueError("Не удалось загрузить ни одной корректной записи из supplies.csv")

        for pile in piles:
            self.pile_repo.save(pile)

    def _upload_temperatures(self, file: TextIOWrapper) -> None:
        """Загружает данные из temperature.csv"""
        reader = csv.DictReader(file)
        readings = []
        for row_num, row in enumerate(reader, start=1):
            try:
                measurement_date = datetime.strptime(row["Дата акта"], "%Y-%m-%d").date()
                reading = TemperatureReading(
                    pile_id=int(row["Штабель"]),
                    warehouse_id=int(row["Склад"]),
                    measurement_date=measurement_date,
                    temperature=float(row["Максимальная температура"]),
                    picket=row.get("Пикет"),
                    shift=int(row["Смена"]) if row.get("Смена") else None,
                )
                readings.append(reading)
                logger.debug(f"Загружена запись temperature.csv: pile_id={reading.pile_id}, date={measurement_date}")
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Пропущена строка {row_num} в temperature.csv: ошибка парсинга — {e}. Строка: {row}"
                )
                continue

        if not readings:
            raise ValueError("Не удалось загрузить ни одной корректной записи из temperature.csv")

        self.temperature_repo.save_batch(readings)

    def _upload_fires(self, file: TextIOWrapper) -> None:
        """Загружает данные из fires.csv"""
        reader = csv.DictReader(file)
        incidents = []
        for row_num, row in enumerate(reader, start=1):
            try:
                doc_date = self._parse_datetime_flexible(row["Дата составления"])
                fire_start = self._parse_datetime_flexible(row["Дата начала"])

                incident = FireIncident(
                    pile_id=int(row["Штабель"]),
                    warehouse_id=int(row["Склад"]),
                    actual_date=fire_start.date(),
                    document_date=doc_date.date(),
                    weight_act=float(row["Вес по акту, тн"]),
                )
                incidents.append(incident)
                logger.debug(f"Загружена запись fires.csv: pile_id={incident.pile_id}, fire_date={fire_start.date()}")
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Пропущена строка {row_num} в fires.csv: ошибка парсинга — {e}. Строка: {row}"
                )
                continue

        if not incidents:
            raise ValueError("Не удалось загрузить ни одной корректной записи из fires.csv")

        self.fire_repo.save_batch(incidents)

    def _upload_weather(self, file: TextIOWrapper) -> None:
        """Загружает данные из weather.csv (ежечасные) и агрегирует по дням"""
        reader = csv.DictReader(file)
        daily_data = {}
        for row_num, row in enumerate(reader, start=1):
            try:
                dt = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
                date_key = dt.date()
                temp = float(row["t"])
                humidity = float(row["humidity"])

                if date_key not in daily_data:
                    daily_data[date_key] = {"temps": [], "humidities": []}
                daily_data[date_key]["temps"].append(temp)
                daily_data[date_key]["humidities"].append(humidity)
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Пропущена строка {row_num} в weather.csv: ошибка парсинга — {e}. Строка: {row}"
                )
                continue

        if not daily_data:
            raise ValueError("Не удалось загрузить ни одной корректной записи из weather.csv")

        weathers = []
        for date_key, values in daily_data.items():
            avg_temp = sum(values["temps"]) / len(values["temps"])
            avg_humidity = sum(values["humidities"]) / len(values["humidities"])
            weather = WeatherData(date=date_key, air_temperature=avg_temp, humidity=avg_humidity)
            weathers.append(weather)
            logger.debug(f"Агрегирована погода за {date_key}")

        self.weather_repo.save_batch(weathers)

    def _parse_datetime_flexible(self, date_str: str) -> datetime:
        """Парсит дату с поддержкой форматов с и без времени"""
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Не удалось распознать дату: {date_str}")