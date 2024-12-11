from datetime import time, datetime

class TimeInterval:
    def __init__(self, start: time, end: time):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"{self.start.strftime('%H:%M')} - {self.end.strftime('%H:%M')}"

    def overlaps(self, other):
        return self.start < other.end and self.end > other.start

class Driver:
    def __init__(self, name: str):
        self.name = name
        self.schedule = {}  # Словарь для хранения расписания на каждый день недели

    def add_work_interval(self, day: str, interval: TimeInterval, bus: str):
        if day not in self.schedule:
            self.schedule[day] = {'work': [], 'breaks': []}
        self.schedule[day]['work'].append((interval, bus))

    def add_break_interval(self, day: str, interval: TimeInterval):
        if day not in self.schedule:
            self.schedule[day] = {'work': [], 'breaks': []}
        self.schedule[day]['breaks'].append(interval)

    def check_overlaps(self, day: str):
        work_intervals = [interval for interval, _ in self.schedule[day]['work']]
        break_intervals = self.schedule[day]['breaks']
        for work in work_intervals:
            for break_time in break_intervals:
                if work.overlaps(break_time):
                    return False
        return True

    def __repr__(self):
        result = f"Driver: {self.name}\n"
        for day, intervals in self.schedule.items():
            result += f"{day}:\n"
            result += "  Work intervals:\n"
            for interval, bus in intervals['work']:
                result += f"    {interval} (Bus: {bus})\n"
            result += "  Break intervals:\n"
            for interval in intervals['breaks']:
                result += f"    {interval}\n"
        return result

# Пример использования
driver1 = Driver(name="John Doe")
driver1.add_work_interval('Monday', TimeInterval(start=time(9, 0), end=time(12, 0)), bus="Bus 1")
driver1.add_work_interval('Monday', TimeInterval(start=time(13, 0), end=time(18, 0)), bus="Bus 2")
driver1.add_break_interval('Monday', TimeInterval(start=time(12, 0), end=time(13, 0)))

driver2 = Driver(name="Jane Smith")
driver2.add_work_interval('Tuesday', TimeInterval(start=time(8, 0), end=time(11, 0)), bus="Bus 3")
driver2.add_work_interval('Tuesday', TimeInterval(start=time(12, 0), end=time(17, 0)), bus="Bus 4")
driver2.add_break_interval('Tuesday', TimeInterval(start=time(11, 0), end=time(12, 0)))

print(driver1)
print(driver2)
