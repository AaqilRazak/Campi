import re

def test_event_pattern():
    # Updated pattern to be more flexible
    pattern = r"what(?:'s| is)?(?: fun)?(?: events?)?(?: are)? happening(?: today| tonight| now)\??"
    test_strings = [
        "What fun events are happening today?",
        "What events are happening today?",
        "What's happening today?",
        "What is happening tonight?",
        "What fun events are happening now?",
        "What's happening now?",
        "What is happening today?"
    ]

    print("Testing event regex pattern:")
    print("-" * 40)
    for test in test_strings:
        match = re.match(pattern, test.lower())
        print(f"Testing: '{test}'")
        print(f"Match result: {bool(match)}\n")

if __name__ == "__main__":
    test_event_pattern()