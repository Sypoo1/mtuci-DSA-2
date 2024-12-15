"""
Система составления расписания для автобусного парка с использованием генетического алгоритма.

Модуль реализует автоматическое составление расписания для водителей автобусов с учетом
различных ограничений и требований к рабочему времени.

Основные характеристики:
- 8 автобусов в парке
- 12 водителей (6 работают по 8 часов, 6 по 12 часов)
- Три группы 12-часовых водителей с разными днями работы
- Учет выходных дней и пиковых часов
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Системные константы
NUM_BUSES = 8
NUM_DRIVERS = 12
NUM_8HR_DRIVERS = 6
NUM_12HR_DRIVERS = NUM_DRIVERS - NUM_8HR_DRIVERS
SHIFT_DURATIONS = {"8hr": 8, "12hr": 12}
DAYS_OF_WEEK = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]
TIME_SLOTS = range(24)

# Параметры генетического алгоритма
POPULATION_SIZE = 100
MAX_GENERATIONS = 1000
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.9
MAX_GENERATIONS_WITHOUT_IMPROVING = 1000
ELITE_SIZE = POPULATION_SIZE // 5


def is_rest_day(driver_id: int, day_idx: int) -> bool:
    """
    Определяет, является ли день выходным для конкретного водителя.

    Args:
        driver_id: Идентификатор водителя
        day_idx: Индекс дня недели

    Returns:
        bool: True если день является выходным для водителя
    """
    if driver_id < NUM_8HR_DRIVERS:
        return DAYS_OF_WEEK[day_idx] in ["Суббота", "Воскресенье"]

    elif driver_id < NUM_8HR_DRIVERS + 2:
        return DAYS_OF_WEEK[day_idx] not in ["Понедельник", "Четверг", "Воскресенье"]

    elif driver_id < NUM_8HR_DRIVERS + 4:
        return DAYS_OF_WEEK[day_idx] not in ["Вторник", "Пятница"]

    else:
        return DAYS_OF_WEEK[day_idx] not in ["Среда", "Суббота"]


def adaptive_mutation_rate(generations_without_improvement: int) -> float:
    """
    Вычисляет адаптивную вероятность мутации на основе стагнации алгоритма.

    Args:
        generations_without_improvement: Количество поколений без улучшения

    Returns:
        float: Вероятность мутации
    """
    base_rate = 0.1
    return min(base_rate * (1 + generations_without_improvement / 10), 0.5)


def two_point_crossover(parent1: list, parent2: list) -> list:
    """
    Выполняет двухточечный кроссовер между двумя родительскими расписаниями.

    Args:
        parent1: Первое родительское расписание
        parent2: Второе родительское расписание

    Returns:
        list: Новое расписание после кроссовера
    """
    point1 = random.randint(0, len(parent1) - 2)
    point2 = random.randint(point1 + 1, len(parent1) - 1)
    return parent1[:point1] + parent2[point1:point2] + parent1[point2:]


def check_shift_overlap(schedule: list) -> int:
    """
    Проверяет наличие пересечений смен водителей на одном автобусе.

    Args:
        schedule: Расписание для проверки

    Returns:
        int: Штраф за найденные пересечения
    """
    penalty = 0
    for day_schedule in schedule:
        bus_shifts = {}
        for shift in day_schedule:
            if not shift["rest"]:
                bus = shift["bus"]
                if bus not in bus_shifts:
                    bus_shifts[bus] = []
                bus_shifts[bus].append((shift["start"], shift["end"], shift["driver"]))

        for bus_id, shifts in bus_shifts.items():
            shifts.sort()
            for i in range(len(shifts) - 1):
                if shifts[i][1] > shifts[i + 1][0]:
                    penalty += 30
    return penalty


def fitness(schedule: list) -> float:
    """
    Оценивает качество расписания на основе штрафов и бонусов.

    Args:
        schedule: Расписание для оценки

    Returns:
        float: Оценка качества расписания
    """
    PENALTIES = {
        "bus_shortage": 10,
        "weekend_work": 15,
        "rest_violation": 20,
        "peak_hours_shortage": 25,
        "shift_overlap": 30,
        "no_workers_day": 10000,
    }

    BONUSES = {
        "weekend_rest": 150,
        "proper_rest_12hr": 140,
    }

    PEAK_HOURS = {"morning": range(7, 10), "evening": range(17, 20)}

    penalty = 0
    bonus = 0
    bus_coverage = {day: {hour: [] for hour in TIME_SLOTS} for day in DAYS_OF_WEEK}

    for day_idx, daily_schedule in enumerate(schedule):
        working_drivers = sum(
            1 for driver_schedule in daily_schedule if not driver_schedule["rest"]
        )
        if working_drivers == 0:
            penalty += PENALTIES["no_workers_day"]

    weekend_rest_violation = False
    for day_idx, day in enumerate(DAYS_OF_WEEK):
        if day in ["Суббота", "Воскресенье"]:
            for driver_schedule in schedule[day_idx]:
                if (
                    driver_schedule["driver"] < NUM_8HR_DRIVERS
                    and not driver_schedule["rest"]
                ):
                    weekend_rest_violation = True
                    break

    if not weekend_rest_violation:
        bonus += BONUSES["weekend_rest"]

    for driver_id in range(NUM_8HR_DRIVERS, NUM_DRIVERS):
        proper_rest = True
        for day_idx in range(1, len(DAYS_OF_WEEK)):
            if not schedule[day_idx][driver_id]["rest"]:
                for prev_day in range(max(0, day_idx - 2), day_idx):
                    if not schedule[prev_day][driver_id]["rest"]:
                        proper_rest = False
                        break
        if proper_rest:
            bonus += BONUSES["proper_rest_12hr"]

    penalty += check_shift_overlap(schedule)

    for day_idx, daily_schedule in enumerate(schedule):
        for driver_schedule in daily_schedule:
            if driver_schedule["rest"]:
                continue

            bus = driver_schedule["bus"]
            start, end = driver_schedule["start"], driver_schedule["end"]

            if bus is not None:
                hours = range(start, end + 1 if end >= start else end + 24)
                for hour in hours:
                    hour = hour % 24
                    bus_coverage[DAYS_OF_WEEK[day_idx]][hour].append(bus)

            if driver_schedule["driver"] < NUM_8HR_DRIVERS and DAYS_OF_WEEK[
                day_idx
            ] in ["Суббота", "Воскресенье"]:
                penalty += PENALTIES["weekend_work"]

            if driver_schedule["driver"] >= NUM_8HR_DRIVERS:
                if day_idx > 0:
                    prev_day = schedule[day_idx - 1]
                    for prev_driver in prev_day:
                        if (
                            prev_driver["driver"] == driver_schedule["driver"]
                            and not prev_driver["rest"]
                        ):
                            penalty += PENALTIES["rest_violation"]

    for day, coverage in bus_coverage.items():
        for hour, buses in coverage.items():
            buses_working = len(set(buses))
            shortage = max(0, NUM_BUSES - buses_working)

            if hour in PEAK_HOURS["morning"] or hour in PEAK_HOURS["evening"]:
                penalty += shortage * PENALTIES["peak_hours_shortage"]
            else:
                if 6 <= hour <= 22:
                    penalty += shortage * PENALTIES["bus_shortage"]

    return bonus - penalty


def generate_random_schedule() -> list:
    """
    Генерирует случайное начальное расписание.

    Returns:
        list: Случайное расписание
    """
    schedule = []
    for day_idx, day in enumerate(DAYS_OF_WEEK):
        daily_schedule = []
        for driver_id in range(NUM_DRIVERS):
            if is_rest_day(driver_id, day_idx):
                daily_schedule.append(
                    {
                        "driver": driver_id,
                        "bus": None,
                        "start": None,
                        "end": None,
                        "rest": True,
                    }
                )
            else:
                bus = random.randint(0, NUM_BUSES - 1)
                shift_type = "8hr" if driver_id < NUM_8HR_DRIVERS else "12hr"
                start_time = (
                    random.randint(6, 10)
                    if shift_type == "8hr"
                    else random.randint(0, 23)
                )
                end_time = (start_time + SHIFT_DURATIONS[shift_type]) % 24
                daily_schedule.append(
                    {
                        "driver": driver_id,
                        "bus": bus,
                        "start": start_time,
                        "end": end_time,
                        "rest": False,
                    }
                )
        schedule.append(daily_schedule)
    return schedule


def mutate(schedule: list) -> list:
    """
    Выполняет мутацию расписания.

    Args:
        schedule: Исходное расписание

    Returns:
        list: Мутированное расписание
    """
    day_idx = random.randint(0, len(schedule) - 1)
    driver_idx = random.randint(0, NUM_DRIVERS - 1)

    if not schedule[day_idx][driver_idx]["rest"]:
        shift_type = "8hr" if driver_idx < NUM_8HR_DRIVERS else "12hr"
        schedule[day_idx][driver_idx]["bus"] = random.randint(0, NUM_BUSES - 1)
        schedule[day_idx][driver_idx]["start"] = (
            random.randint(6, 10) if shift_type == "8hr" else random.randint(0, 23)
        )
        schedule[day_idx][driver_idx]["end"] = (
            schedule[day_idx][driver_idx]["start"] + SHIFT_DURATIONS[shift_type]
        ) % 24

    return schedule


def genetic_algorithm() -> list:
    """
    Реализует генетический алгоритм для поиска оптимального расписания.

    Returns:
        list: Лучшее найденное расписание
    """
    population = [generate_random_schedule() for _ in range(POPULATION_SIZE)]
    best_solution = None
    best_fitness = float("-inf")
    generations_without_improvement = 0

    for generation in range(MAX_GENERATIONS):
        current_mutation_rate = adaptive_mutation_rate(generations_without_improvement)
        fitness_values = [fitness(schedule) for schedule in population]
        population_with_fitness = list(zip(population, fitness_values))
        population_with_fitness.sort(key=lambda x: x[1], reverse=True)

        current_best, current_fitness = population_with_fitness[0]

        if current_fitness > best_fitness:
            best_solution = current_best
            best_fitness = current_fitness
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

        next_generation = [ind for ind, _ in population_with_fitness[:ELITE_SIZE]]

        while len(next_generation) < POPULATION_SIZE:
            if random.random() < CROSSOVER_RATE:
                parents = random.sample(
                    population_with_fitness[: int(POPULATION_SIZE * 0.4)], 2
                )
                child = two_point_crossover(parents[0][0], parents[1][0])
            else:
                child = random.choice(
                    population_with_fitness[: int(POPULATION_SIZE * 0.4)]
                )[0]

            if random.random() < current_mutation_rate:
                child = mutate(child)

            next_generation.append(child)

        population = next_generation

        if generation % 50 == 0:
            print(f"Поколение {generation}: Лучший фитнес = {current_fitness}")
            print(f"Поколений без улучшения: {generations_without_improvement}")

        if generations_without_improvement >= MAX_GENERATIONS_WITHOUT_IMPROVING:
            print(
                f"Досрочная остановка: нет улучшений в течение {MAX_GENERATIONS_WITHOUT_IMPROVING} поколений"
            )
            break

    return best_solution


def generate_schedule_dataframe(schedule: list) -> pd.DataFrame:
    """
    Создает DataFrame с расписанием в читаемом формате.

    Args:
        schedule: Расписание для отображения

    Returns:
        pd.DataFrame: Таблица с расписанием
    """
    driver_labels = [f"Водитель {d + 1}" for d in range(NUM_DRIVERS)]
    shifts = ["8hr" if d < NUM_8HR_DRIVERS else "12hr" for d in range(NUM_DRIVERS)]

    schedule_df = pd.DataFrame(index=driver_labels, columns=["Смена"] + DAYS_OF_WEEK)
    schedule_df["Смена"] = shifts

    for day_idx, daily_schedule in enumerate(schedule):
        for driver_schedule in daily_schedule:
            driver = f"Водитель {driver_schedule['driver'] + 1}"
            if driver_schedule["rest"]:
                schedule_df.loc[driver, DAYS_OF_WEEK[day_idx]] = "Отдых"
            else:
                bus = driver_schedule["bus"]
                start = driver_schedule["start"]
                end = driver_schedule["end"]
                schedule_df.loc[driver, DAYS_OF_WEEK[day_idx]] = (
                    f"Автобус {bus + 1} ({start:02d}:00 - {end:02d}:00)"
                )

    return schedule_df.sort_values(by="Смена", ascending=False)


best_schedule = genetic_algorithm()
schedule_df = generate_schedule_dataframe(best_schedule)
print("\nЛучшее найденное расписание:")
schedule_df
