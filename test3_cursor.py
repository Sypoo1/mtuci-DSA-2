from datetime import datetime, timedelta
from typing import List, Tuple

# Константы
PEAK_HOURS = [
    (datetime.strptime("07:00", "%H:%M").time(), datetime.strptime("09:00", "%H:%M").time()),
    (datetime.strptime("17:00", "%H:%M").time(), datetime.strptime("19:00", "%H:%M").time())
]

TRIP_BASE_DURATION = 90  # минут
TRIP_VARIABILITY = 10  # минут
PEAK_ADDITIONAL_TIME = 5  # минут
CHANGEOVER_DURATION = 15  # минут

# Класс Водителя
class Driver:
    def __init__(self, driver_id: int, shift_hours: int):
        self.driver_id = driver_id
        self.shift_hours = shift_hours
        self.schedule = []  # список расписаний (начало, конец, автобус)

    def add_shift(self, start: datetime, end: datetime, bus_id: int):
        self.schedule.append((start, end, bus_id))

# Класс Автобуса
class Bus:
    def __init__(self, bus_id: int):
        self.bus_id = bus_id
        self.schedule = []  # список расписаний (начало, конец, водитель)

    def add_trip(self, start: datetime, end: datetime, driver_id: int):
        self.schedule.append((start, end, driver_id))

# Класс Расписания
class Schedule:
    def __init__(self, max_drivers: int, max_buses: int):
        self.max_drivers = max_drivers
        self.max_buses = max_buses
        self.drivers: List[Driver] = []
        self.buses: List[Bus] = []
        self.initialize_resources()

    def initialize_resources(self):
        for i in range(1, self.max_drivers + 1):
            shift_hours = 12 if i % 2 == 0 else 8
            self.drivers.append(Driver(driver_id=i, shift_hours=shift_hours))
        for i in range(1, self.max_buses + 1):
            self.buses.append(Bus(bus_id=i))

    def is_peak_hour(self, current_time: datetime) -> bool:
        return any(start <= current_time.time() < end for start, end in PEAK_HOURS)

    def get_trip_duration(self, start_time: datetime) -> int:
        base_duration = TRIP_BASE_DURATION + (5 if self.is_peak_hour(start_time) else 0)
        return base_duration

    def generate_trips(self, start_time: datetime, end_time: datetime) -> List[Tuple[datetime, datetime]]:
        trips = []
        current_time = start_time
        while current_time < end_time:
            duration = self.get_trip_duration(current_time)
            trip_end = current_time + timedelta(minutes=duration)
            trips.append((current_time, trip_end))
            current_time = trip_end + timedelta(minutes=CHANGEOVER_DURATION)
        return trips

    def assign_trips(self):
        week_start = datetime.strptime("2023-04-24 00:00", "%Y-%m-%d %H:%M")
        week_end = week_start + timedelta(days=7)
        trips = self.generate_trips(week_start, week_end)

        for trip_start, trip_end in trips:
            assigned = False
            for bus in self.buses:
                if all(not (t_start < trip_end and trip_start < t_end) for t_start, t_end, _ in bus.schedule):
                    for driver in self.drivers:
                        if all(not (d_start < trip_end and trip_start < d_end) for d_start, d_end, _ in driver.schedule):
                            bus.add_trip(trip_start, trip_end, driver.driver_id)
                            driver.add_shift(trip_start, trip_end, bus.bus_id)
                            assigned = True
                            break
                    if assigned:
                        break
            if not assigned:
                print(f"Не удалось назначить поездку: {trip_start} - {trip_end}")

    def print_schedule(self):
        for driver in self.drivers:
            print(f"Водитель {driver.driver_id} ({driver.shift_hours} часов):")
            for shift in driver.schedule:
                start, end, bus_id = shift
                print(f"  Работа с {start.strftime('%H:%M')} до {end.strftime('%H:%M')} на автобусе {bus_id}")
            print()

        for bus in self.buses:
            print(f"Автобус {bus.bus_id}:")
            for trip in bus.schedule:
                start, end, driver_id = trip
                print(f"  Поездка с {start.strftime('%H:%M')} до {end.strftime('%H:%M')} водителем {driver_id}")
            print()

# Основная функция
def main():
    max_drivers = 12  # Максимальное количество водителей
    max_buses = 3     # Максимальное количество автобусов

    schedule = Schedule(max_drivers, max_buses)
    schedule.assign_trips()
    schedule.print_schedule()

if __name__ == "__main__":
    main()
