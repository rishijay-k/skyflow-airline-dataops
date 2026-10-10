import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)

OUTPUT_FILE = Path("data/flight_events_1000.jsonl")

AIRPORTS = [
    "AMS", "JFK", "LHR", "DEL", "CDG",
    "FRA", "DXB", "SIN", "BOM", "BLR"
]

EVENT_TYPES = [
    "FLIGHT_SCHEDULED",
    "GATE_ASSIGNED",
    "BOARDING_STARTED",
    "DEPARTURE_DELAYED",
    "DEPARTED",
    "ARRIVED"
]

AIRCRAFT_TYPES = [
    "Boeing 737-800",
    "Boeing 787-9",
    "Airbus A320",
    "Airbus A321neo",
    "Airbus A330-300"
]

FLIGHT_STATUSES = [
    "SCHEDULED",
    "BOARDING",
    "DELAYED",
    "DEPARTED",
    "ARRIVED"
]


def create_event():
    origin, destination = random.sample(AIRPORTS, 2)

    event_type = random.choice(EVENT_TYPES)

    delay_minutes = (
        random.randint(5, 180)
        if event_type == "DEPARTURE_DELAYED"
        else 0
    )

    event_time = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    return {
        "event_id": str(uuid.uuid4()),
        "flight_id": f"SF{random.randint(1000, 9999)}",
        "origin_airport": origin,
        "destination_airport": destination,
        "event_type": event_type,
        "event_timestamp": event_time.isoformat(),
        "delay_minutes": delay_minutes,
        "aircraft_type": random.choice(AIRCRAFT_TYPES),
        "flight_status": random.choice(FLIGHT_STATUSES)
    }


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for _ in range(1000):
            event = create_event()
            file.write(json.dumps(event) + "\n")

    print("")
    print("SKYFLOW AIRLINE EVENT GENERATOR")
    print("-------------------------------")
    print("Status: SUCCESS")
    print("Events generated: 1000")
    print(f"Output file: {OUTPUT_FILE}")
    print("")


if __name__ == "__main__":
    main()
