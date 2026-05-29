"""
Юнит-тесты для основных модулей программы.
Запуск: python -m unittest tests.py
"""
import unittest
import os
import sys

# Добавляем родительский каталог в путь, чтобы импортировать модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.airport import Airport
from models.aircraft import Aircraft
from models.flight import Flight
from utils.validators import Validator


class TestAirportModel(unittest.TestCase):
    """Тесты класса Airport."""

    def test_valid_airport_creation(self):
        """Корректное создание аэропорта."""
        airport = Airport(name="Шереметьево", city="Москва",
                          iata_code="SVO", country="Россия")
        valid, msg = airport.validate()
        self.assertTrue(valid, msg)

    def test_invalid_iata_code(self):
        """Некорректный IATA-код (не 3 символа)."""
        airport = Airport(name="Test", city="Test", iata_code="AB")
        valid, msg = airport.validate()
        self.assertFalse(valid)

    def test_empty_name(self):
        """Пустое название аэропорта."""
        airport = Airport(name="", city="Москва", iata_code="ABC")
        valid, msg = airport.validate()
        self.assertFalse(valid)

    def test_iata_must_be_letters(self):
        """IATA-код должен состоять из букв."""
        airport = Airport(name="Test", city="Test", iata_code="123")
        valid, msg = airport.validate()
        self.assertFalse(valid)

    def test_to_dict(self):
        """Сериализация в словарь."""
        airport = Airport(name="Test", city="City", iata_code="ABC")
        data = airport.to_dict()
        self.assertEqual(data["name"], "Test")
        self.assertEqual(data["iata_code"], "ABC")


class TestAircraftModel(unittest.TestCase):
    """Тесты класса Aircraft."""

    def test_valid_aircraft_creation(self):
        """Корректное создание самолёта."""
        aircraft = Aircraft(model="Boeing 737", registration_number="RA-12345",
                            capacity=180, aircraft_type="Пассажирский")
        valid, msg = aircraft.validate()
        self.assertTrue(valid, msg)

    def test_zero_capacity(self):
        """Нулевая вместимость недопустима."""
        aircraft = Aircraft(model="Test", registration_number="RA-001",
                            capacity=0)
        valid, msg = aircraft.validate()
        self.assertFalse(valid)

    def test_negative_capacity_raises(self):
        """Отрицательная вместимость через сеттер вызывает ошибку."""
        aircraft = Aircraft(model="Test", registration_number="RA-001",
                            capacity=100)
        with self.assertRaises(ValueError):
            aircraft.capacity = -10

    def test_invalid_type(self):
        """Недопустимый тип воздушного судна."""
        aircraft = Aircraft(model="Test", registration_number="RA-001",
                            capacity=100, aircraft_type="Космический")
        valid, msg = aircraft.validate()
        self.assertFalse(valid)


class TestFlightModel(unittest.TestCase):
    """Тесты класса Flight."""

    def test_valid_flight_creation(self):
        """Корректное создание рейса."""
        flight = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 08:00",
            arrival_time="2026-05-20 10:00",
        )
        valid, msg = flight.validate()
        self.assertTrue(valid, msg)

    def test_same_airports(self):
        """Совпадение аэропортов отправления и прибытия."""
        flight = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=1,
            aircraft_id=1,
            departure_time="2026-05-20 08:00",
            arrival_time="2026-05-20 10:00",
        )
        valid, msg = flight.validate()
        self.assertFalse(valid)

    def test_arrival_before_departure(self):
        """Прибытие раньше отправления — некорректно."""
        flight = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 10:00",
            arrival_time="2026-05-20 08:00",
        )
        valid, msg = flight.validate()
        self.assertFalse(valid)

    def test_duration_calculation(self):
        """Расчёт продолжительности рейса."""
        flight = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 08:00",
            arrival_time="2026-05-20 10:30",
        )
        self.assertEqual(flight.get_duration_minutes(), 150)
        self.assertEqual(flight.get_duration_formatted(), "2 ч 30 мин")

    def test_overlap_detection(self):
        """Обнаружение пересечения рейсов по времени."""
        flight1 = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 08:00",
            arrival_time="2026-05-20 10:00",
        )
        flight2 = Flight(
            flight_number="SU200",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 09:00",
            arrival_time="2026-05-20 11:00",
        )
        self.assertTrue(flight1.overlaps_with(flight2))

    def test_no_overlap(self):
        """Рейсы без пересечения."""
        flight1 = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 08:00",
            arrival_time="2026-05-20 10:00",
        )
        flight2 = Flight(
            flight_number="SU200",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 11:00",
            arrival_time="2026-05-20 13:00",
        )
        self.assertFalse(flight1.overlaps_with(flight2))

    def test_invalid_status(self):
        """Недопустимый статус рейса."""
        flight = Flight(
            flight_number="SU100",
            departure_airport_id=1,
            arrival_airport_id=2,
            aircraft_id=1,
            departure_time="2026-05-20 08:00",
            arrival_time="2026-05-20 10:00",
        )
        with self.assertRaises(ValueError):
            flight.status = "Несуществующий"


class TestValidator(unittest.TestCase):
    """Тесты класса Validator."""

    def test_valid_datetime(self):
        valid, _ = Validator.validate_datetime("2026-05-20 08:00")
        self.assertTrue(valid)

    def test_invalid_datetime(self):
        valid, _ = Validator.validate_datetime("20.05.2026 8:00")
        self.assertFalse(valid)

    def test_valid_iata(self):
        valid, _ = Validator.validate_iata("SVO")
        self.assertTrue(valid)

    def test_invalid_iata(self):
        valid, _ = Validator.validate_iata("SV")
        self.assertFalse(valid)

    def test_positive_int(self):
        valid, _ = Validator.validate_positive_int("100")
        self.assertTrue(valid)
        valid, _ = Validator.validate_positive_int("-5")
        self.assertFalse(valid)

    def test_non_negative_float(self):
        valid, _ = Validator.validate_non_negative_float("99.99")
        self.assertTrue(valid)
        valid, _ = Validator.validate_non_negative_float("0")
        self.assertTrue(valid)
        valid, _ = Validator.validate_non_negative_float("-1.5")
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
