from datetime import datetime, timedelta

def generate_schedule(start_time: str, work_duration: int = 12, trip_duration: int = 105, rest_duration: int = 10):
    
    start = datetime.strptime(start_time, "%H:%M")
    end_time = start + timedelta(hours=work_duration)

    current_time = start
    trips = []
    trip_count = 0

    while current_time < end_time:
        
        trip_start = current_time
        trip_end = current_time + timedelta(minutes=trip_duration)

        
        if trip_end > end_time:
            break

        trips.append(f"Trip {trip_count + 1}: {trip_start.strftime('%H:%M')} - {trip_end.strftime('%H:%M')}")
        trip_count += 1
        current_time = trip_end

        
        if trip_count % 2 == 0:
            rest_start = current_time
            rest_end = current_time + timedelta(minutes=rest_duration)

            if rest_end > end_time:
                break

            trips.append(f"Rest: {rest_start.strftime('%H:%M')} - {rest_end.strftime('%H:%M')}")
            current_time = rest_end

    return trips

print("\nDriver 1\n")
schedule = generate_schedule("00:00")
for entry in schedule:
    print(entry)

print("\nDriver 2\n")
schedule = generate_schedule("03:30")
for entry in schedule:
    print(entry)


print("\nDriver 3\n")
schedule = generate_schedule("11:05")
for entry in schedule:
    print(entry)

print("\nDriver 4\n")
schedule = generate_schedule("14:35")
for entry in schedule:
    print(entry)