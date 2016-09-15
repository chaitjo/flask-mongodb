from requests import get, post, put, delete
import json
from datetime import datetime

with open("dataset.json", "r") as data_file:
	data = data_file.readlines()
	for entry in data:
		entry = json.loads(entry)
		post("http://127.0.0.1:5000/api", json=entry).json()