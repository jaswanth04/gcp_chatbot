import time

class Event:
    def __init__(self, event_message):
        self.event_id = str(uuid.uuid4())
        self.event_time = time.time()
        self.event_name = self.__class__.__name__
        self.event_message = event_message
    
    def to_dict(self):
        return {
            "event_id": self.event_id,
            "event_time": self.event_time,
            "event_name": self.event_name,
            "event_message": self.event_message
        }

class ProductQueryEvent(Event):
    def __init__(self, source_session_id, source_timestamp, query):
        event_message = {
            "source_session_id": source_session_id,
            "source_timestamp": source_timestamp,
            "query": query
        }

        super().__init__(event_message)


def main():
    # Creating an instance of ProductQueryEvent
    product_query_event = ProductQueryEvent(
        source_session_id=str(uuid.uuid4()),
        source_timestamp=time.time(),
        query="How are you?"
    )

    # Convert event instance to dictionary
    event_dict = product_query_event.to_dict()

    # Convert event dictionary to JSON string
    event_json = json.dumps(event_dict)

    print(event_json)

if __name__ == "__main__":
    main()
