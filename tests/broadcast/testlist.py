testlist = [
    {"test_id": 1,
     "port": 5000,
     "service_id": "lounge_tivo",
     "service_type": "virginmedia_tivo",
     "expected_result": True},
    {"test_id": 2,
     "port": 8080,
     "service_id": "lounge_tivo",
     "service_type": "virginmedia_tivo",
     "expected_result": False},
    {"test_id": 3,
     "port": 5000,
     "service_id": "lounge_tivo",
     "service_type": "tivo",
     "expected_result": False}
]