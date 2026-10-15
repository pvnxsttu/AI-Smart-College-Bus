
import pandas as pd
import random

random.seed(42)
rows = []

for _ in range(1000):
    distance = round(random.uniform(0.5, 15), 2)
    speed = round(random.uniform(10, 50), 2)
    hour = random.randint(6, 22)
    traffic = random.choice(["low", "medium", "high"])
    stops = random.randint(0, 8)

    traffic_delay = {"low": 0, "medium": 2, "high": 5}[traffic]
    stop_delay = stops * 1.5
    travel_time = (distance / speed) * 60 + traffic_delay + stop_delay
    travel_time += random.uniform(-1, 1)

    rows.append([
        distance, speed, hour, traffic, stops,
        round(max(0.5, travel_time), 2)
    ])

df = pd.DataFrame(rows, columns=[
    "distance_km", "speed_kmh", "hour", "traffic",
    "stops_remaining", "travel_time_min"
])

df.to_csv("data/bus_data.csv", index=False)
print("Generated 1000 simulated bus-trip records.")
print(df.head())