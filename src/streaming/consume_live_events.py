import json
import threading

from google.cloud import pubsub_v1


PROJECT_ID = "skyflow-511113"
SUBSCRIPTION_ID = "skyflow-flight-events-sub"

MAX_MESSAGES = 20
WAIT_TIMEOUT_SECONDS = 120


REQUIRED_FIELDS = {
    "event_id",
    "flight_id",
    "origin_airport",
    "destination_airport",
    "event_type",
    "event_timestamp",
    "delay_minutes",
    "aircraft_type",
    "flight_status",
}


subscriber = pubsub_v1.SubscriberClient()

subscription_path = subscriber.subscription_path(
    PROJECT_ID,
    SUBSCRIPTION_ID,
)

received_count = 0

done = threading.Event()
lock = threading.Lock()


def callback(message):

    global received_count

    try:

        event = json.loads(
            message.data.decode("utf-8")
        )

        missing_fields = (
            REQUIRED_FIELDS - event.keys()
        )

        if missing_fields:

            print("")
            print(
                "INVALID EVENT | "
                f"Missing fields: {sorted(missing_fields)}"
            )

            message.nack()

            return

        with lock:

            received_count += 1
            current_number = received_count

        print(
            f"[{current_number:02d}/{MAX_MESSAGES}] "
            f"{event['flight_id']} | "
            f"{event['origin_airport']} -> "
            f"{event['destination_airport']} | "
            f"{event['event_type']:<20} | "
            f"Delay: {event['delay_minutes']:>3} min | "
            f"Message ID: {message.message_id}"
        )

        message.ack()

        if current_number >= MAX_MESSAGES:
            done.set()

    except Exception as error:

        print("")
        print("MESSAGE PROCESSING FAILED")
        print(type(error).__name__)
        print(error)
        print("")

        message.nack()


def main():

    print("")
    print("SKYFLOW LIVE EVENT CONSUMER")
    print("--------------------------------------------------")
    print(f"Project:      {PROJECT_ID}")
    print(f"Subscription: {SUBSCRIPTION_ID}")
    print(f"Target:       {MAX_MESSAGES} events")
    print("--------------------------------------------------")
    print("")
    print("Waiting for flight events...")
    print("")

    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=callback,
    )

    try:

        completed = done.wait(
            timeout=WAIT_TIMEOUT_SECONDS
        )

        if not completed:

            print("")
            print(
                f"Consumer timed out after "
                f"{WAIT_TIMEOUT_SECONDS} seconds."
            )
            print(
                f"Events received: "
                f"{received_count}/{MAX_MESSAGES}"
            )

    except KeyboardInterrupt:

        print("")
        print("Consumer stopped manually.")

    finally:

        streaming_pull_future.cancel()

        try:
            streaming_pull_future.result()
        except Exception:
            pass

        subscriber.close()

    print("")
    print("--------------------------------------------------")

    if received_count >= MAX_MESSAGES:

        print("SKYFLOW STREAMING CONSUMER: SUCCESS")
        print(f"Events consumed: {received_count}")

    else:

        print("SKYFLOW STREAMING CONSUMER: INCOMPLETE")
        print(f"Events consumed: {received_count}")

    print("--------------------------------------------------")
    print("")


if __name__ == "__main__":
    main()
