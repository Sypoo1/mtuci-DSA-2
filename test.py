from datetime import datetime, timedelta
from datetime import datetime, timedelta


def is_peak_hour(current_time: datetime) -> bool:
    for start, end in PEAK_HOURS:
        peak_start = datetime.strptime(start, "%H:%M").time()
        peak_end = datetime.strptime(end, "%H:%M").time()
        if peak_start <= current_time.time() < peak_end:
            return True
    return False


def get_trip_duration(start_time: datetime, base_duration: int = DEFAULT_TRIP_DURATION) -> int:
    """
    Рассчитывает длительность поездки:
    - Увеличивает длительность на 5 минут, если поездка пересекает часы пик.
    """
    end_time = start_time + timedelta(minutes=base_duration)

    if is_peak_hour(start_time) or is_peak_hour(end_time):
        base_duration += 5

    return base_duration


class TimeInterval:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"{self.start.strftime('%H:%M')} - {self.end.strftime('%H:%M')}"

    def overlaps(self, other):
        return self.start < other.end and self.end > other.start


class Bus:
    def __init__(self, id: int, capacity: int = 100, speed: int = 60, type: str = "Электробус"):
        self.id = id
        self.capacity = capacity
        self.speed = speed
        self.type = type


class Driver:
    def __init__(self, id: int, bus_id: int, work_time: [(TimeInterval, int)] = None, rest_time: [TimeInterval] = None, type: str = "12_hr", expirience: int = 0):
        self.id = id
        self.bus_id = bus_id
        self.work_time = work_time if  work_time is not None else []
        self.rest_time = rest_time if rest_time is not None else []
        self.type = type
        self.expirience = expirience

    def get_trip_intevals(self):
        return [interval for interval, bus_id in self.work_time]

    def get_last_trip_inteval(self):
        return self.get_trip_intevals()[-1] if self.get_trip_intevals() else None

    def get_work_hours(self):
        if self.type == "12_hr":
            return 12
        elif self.type == "8_hr":
            return 8

        return None

    def get_rest_minutes(self):
        if self.type == "12_hr":
            return 10
        elif self.type == "8_hr":
            return 60
        return None


    def generate_schedule(self, start_time: str):
        self.work_time.clear()

        start = datetime.strptime(start_time, "%H:%M")
        end_time = start + timedelta(hours=self.get_work_hours())

        current_time = start
        trip_count = 0

        while current_time < end_time:
            trip_duration = get_trip_duration(current_time)
            trip_start = current_time
            trip_end = current_time + timedelta(minutes=trip_duration)
            
            if trip_end.time() < trip_start.time():

                self.work_time.append((TimeInterval(trip_start, trip_end), self.bus_id))
                break

            self.work_time.append((TimeInterval(trip_start, trip_end), self.bus_id))

            trip_count += 1
            current_time = trip_end

            if self.type == "12_hr" and trip_count % 2 == 0:
                rest_start = current_time
                rest_end = current_time + timedelta(minutes=self.get_rest_minutes())

                if rest_end.time() < rest_start.time():
                    rest_end = datetime.strptime("00:00", "%H:%M").time()

                    self.rest_time.append(TimeInterval(rest_start, rest_end))
                    break
                
                self.rest_time.append(TimeInterval(rest_start, rest_end))
                current_time = rest_end

def check_continuous_coverage(intervals):
    """
    Проверяет, обеспечивает ли расписание непрерывное покрытие с 00:00 до 00:00 следующего дня.
    """
    intervals.sort(key=lambda x: x.start) 

    # if intervals[0].start != datetime.strptime("00:00", "%H:%M").time():
    #     print(intervals[0])
    #     return False, "00:00", intervals[0].start.strftime("%H:%M")


    for i in range(len(intervals) - 1):
        if intervals[i].end < intervals[i + 1].start and intervals[i].start < intervals[i].end:
            print(intervals[i])
            print(intervals[i + 1])
            return False, intervals[i].end.strftime("%H:%M"), intervals[i + 1].start.strftime("%H:%M")

    if intervals[-1].end.time() < datetime.strptime("23:59", "%H:%M").time() and intervals[-1].start < intervals[-1].end:
        print(intervals[-1])
        return False, intervals[-1].end.strftime("%H:%M"), "23:59"

    # # Преобразуем "23:59" в datetime для корректного сравнения
    # end_of_day = datetime.combine(intervals[-1].end.date(), datetime.strptime("23:59", "%H:%M").time())
    # if intervals[-1].end < end_of_day and intervals[-1].start < intervals[-1].end:
    #     print(intervals[-1])
    #     return False, intervals[-1].end.strftime("%H:%M"), "23:59"


    return True, None, None

def get_all_trips_intervals(drivers):
    intervals = []

    for driver in drivers:
        intervals.extend(driver.get_trip_intevals())

    return intervals



def find_valid_schedule(drivers, drivers_start_time):
    # Генерация всех возможных временных значений с шагом 5 минут
    start_time = datetime.strptime("00:00", "%H:%M")
    end_time = datetime.strptime("23:55", "%H:%M")
    time_step = timedelta(minutes=35)
    
    all_times = []
    current_time = start_time
    while current_time <= end_time:
        all_times.append(current_time.strftime("%H:%M"))
        current_time += time_step

    # Перебор всех комбинаций времени для водителей 4, 3 и 2 (в нужном порядке)
    for time_4 in all_times:  # Сначала меняем время для водителя 4
        drivers_start_time[4] = time_4
        for time_3 in all_times:  # Затем для водителя 3
            drivers_start_time[3] = time_3
            for time_2 in all_times:  # В конце для водителя 2
                drivers_start_time[2] = time_2


                # Генерация расписания для всех водителей
                for driver in drivers:
                    driver.generate_schedule(drivers_start_time[driver.id])

                # Проверка непрерывного покрытия
                all_intervals = get_all_trips_intervals(drivers)
                is_continuous_coverage, start_time, end_time = check_continuous_coverage(all_intervals)

                # Проверка дополнительных условий
                driver_3_last_trip = drivers[2].get_last_trip_inteval()
                if (
                    is_continuous_coverage
                    and driver_3_last_trip
                    and driver_3_last_trip.end < datetime.strptime("23:45", "%H:%M").time()
                    and driver_3_last_trip.start < driver_3_last_trip.end
                ):
                    # Успешный случай
                    return True
                print(drivers_start_time)

    # Если ни одна комбинация не подошла
    return False


def test(drivers_start_time):
    for driver in drivers:
        driver.generate_schedule(drivers_start_time[driver.id])

    # Проверка непрерывного покрытия
    all_intervals = get_all_trips_intervals(drivers)
    is_continuous_coverage, start_time, end_time = check_continuous_coverage(all_intervals)

    # Проверка дополнительных условий
    driver_3_last_trip = drivers[2].get_last_trip_inteval()
    if (
        is_continuous_coverage
        and driver_3_last_trip
        and driver_3_last_trip.end < datetime.strptime("23:45", "%H:%M").time()
        and driver_3_last_trip.start < driver_3_last_trip.end
    ):
        # Успешный случай
        return True
    print(drivers_start_time)
    print(is_continuous_coverage, start_time, end_time)
    return True
