import json
import random
import time
import uuid
from datetime import datetime, timezone

from google.cloud import pubsub_v1


PROJECT_ID = "skyflow-511113"
TOPIC_ID = "skyflow-flight-events"

NUMBER_OF_EVENTS = 20
PUBLISH_INTERVAL_SECONDS = 1
PUBLISH_TIMEOUT_SECONDS = 30


AIRPORTS = [
    "AMS",
    "JFK",
    "LHR",
    "DEL",
    "CDG",
    "FRA",
    "DXB",
    "SIN",
    "BOM",
    "BLR",
]


EVENT_TYPES = [
    "FLIGHT_SCHEDULED",
    "GATE_ASSIGNED",
    "BOARDING_STARTED",
    "DEPARTURE_DELAYED",
    "DEPARTED",
    "ARRIVED",
]


AIRCRAFT_TYPES = [
    "Boeing 737-800",
    "Boeing 787-9",
    "Airbus A320",
    "Airbus A321neo",
    "Airbus A330-300",
]


STATUS_BY_EVENT = {
    "FLIGHT_SCHEDULED": "SCHEDULED",
    "GATE_ASSIGNED": "SCHEDULED",
    "BOARDING_STARTED": "BOARDING",
    "DEPARTURE_DELAYED": "DELAYED",
    "DEPARTED": "DEPARTED",
    "ARRIVED": "ARRIVED",
}


def create_event():

    origin, destination = random.sample(AIRPORTS, 2)

    event_type = random.choice(EVENT_TYPES)

    delay_minutes = (
        random.randint(5, 180)
        if event_type == "DEPARTURE_DELAYED"
        else 0
    )

    return {
        "event_id": str(uuid.uuid4()),
        "flight_id": f"SF{random.randint(1000, 9999)}",
        "origin_airport": origin,
        "destination_airport": destination,
        "event_type": event_type,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "delay_minutes": delay_minutes,
        "aircraft_type": random.choice(AIRCRAFT_TYPES),
        "flight_status": STATUS_BY_EVENT[event_type],
    }


def main():

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(
        PROJECT_ID,
        TOPIC_ID,
    )

    print("")
    print("SKYFLOW LIVE EVENT PRODUCER")
    print("----------------------------------------------")
    print(f"Project: {PROJECT_ID}")
    print(f"Topic:   {TOPIC_ID}")
    print(f"Events:  {NUMBER_OF_EVENTS}")
    print("----------------------------------------------")
    print("")

    published_count = 0

    try:

        for event_number in range(
            1,
            NUMBER_OF_EVENTS + 1
        ):

            event = create_event()

            message = json.dumps(
                event
            ).encode("utf-8")

            future = publisher.publish(
                topic_path,
                message,
                event_type=event["event_type"],
                flight_id=event["flight_id"],
            )

            message_id = future.result(
                timeout=PUBLISH_TIMEOUT_SECONDS
            )

            published_count += 1

            print(
                f"[{event_number:02d}/{NUMBER_OF_EVENTS}] "
                f"{event['flight_id']} | "
                f"{event['origin_airport']} -> "
                f"{event['destination_airport']} | "
                f"{event['event_type']:<20} | "
                f"Message ID: {message_id}"
            )

            time.sleep(
                PUBLISH_INTERVAL_SECONDS
            )

    except Exception as error:

        print("")
        print("PUBLISH FAILED")
        print("----------------------------------------------")
        print(type(error).__name__)
        print(error)
        print("")

        raise

    finally:

        publisher.stop()

    print("")
    print("----------------------------------------------")
    print("SKYFLOW STREAMING PRODUCER: SUCCESS")
    print(f"Published events: {published_count}")
    print("----------------------------------------------")
    print("")


if __name__ == "__main__":
    main()
