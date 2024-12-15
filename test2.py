from datetime import datetime, timedelta

def is_peak_hour(current_time: datetime) -> bool:
    """Check if the current time falls within peak hours."""
    return (current_time.time() >= datetime.strptime("07:00", "%H:%M").time() and 
            current_time.time() < datetime.strptime("09:00", "%H:%M").time()) or \
           (current_time.time() >= datetime.strptime("17:00", "%H:%M").time() and 
            current_time.time() < datetime.strptime("19:00", "%H:%M").time())

def get_trip_duration(start_time: datetime, duration: int) -> int:
    """Determine the trip duration based on peak hours."""
    end_time = start_time + timedelta(minutes=duration)
    
    # Check if the trip overlaps with peak hours
    if is_peak_hour(start_time) or is_peak_hour(end_time):
        return 105  # 105 minutes during peak hours
    else:
        return 100  # 100 minutes otherwise

def generate_schedule(start_time: str, work_duration: int = 12, rest_duration: int = 10):
    start = datetime.strptime(start_time, "%H:%M")
    end_time = start + timedelta(hours=work_duration)

    current_time = start
    trips = []
    trip_count = 0

    while current_time < end_time:
        # Get the trip duration based on current and end time
        trip_duration = get_trip_duration(current_time, 100)  # Initial guess of 100 minutes
        
        trip_start = current_time
        trip_end = current_time + timedelta(minutes=trip_duration)

        if trip_end > end_time:
            break

        trips.append(f"Trip {trip_count + 1}: {trip_start.strftime('%H:%M')} - {trip_end.strftime('%H:%M')}")
        trip_count += 1
        current_time = trip_end

        if trip_count % 2 == 0:  # Rest after every two trips
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