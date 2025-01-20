 
import json
import random
from datetime import datetime, timedelta

def generate_lab_result(test_type):
    if test_type == "glucose":
        value = round(random.uniform(70, 200), 1)
        unit = "mg/dL"
        if value < 70:
            label = "Low glucose level"
        elif value > 140:
            label = "High glucose level"
        else:
            label = "Normal glucose level"
    elif test_type == "hemoglobin":
        value = round(random.uniform(8, 18), 1)
        unit = "g/dL"
        if value < 12:
            label = "Low hemoglobin level"
        elif value > 16:
            label = "High hemoglobin level"
        else:
            label = "Normal hemoglobin level"
    elif test_type == "white_blood_cell":
        value = round(random.uniform(3000, 15000), 0)
        unit = "cells/µL"
        if value < 4000:
            label = "Low white blood cell count"
        elif value > 11000:
            label = "High white blood cell count"
        else:
            label = "Normal white blood cell count"
    else:
        raise ValueError(f"Unknown test type: {test_type}")
    
    return value, unit, label

def generate_data_point():
    test_types = ["glucose", "hemoglobin", "white_blood_cell"]
    test_type = random.choice(test_types)
    value, unit, label = generate_lab_result(test_type)
    
    if test_type == "white_blood_cell":
        text = f"Patient's {test_type} count is {value} {unit}"
    else:
        text = f"Patient's {test_type} level is {value} {unit}"
    
    return {
        "text": text,
        "label": label,
        "timestamp": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
    }

def generate_initial_data(num_samples=1000):
    data = [generate_data_point() for _ in range(num_samples)]
    return data

if __name__ == "__main__":
    initial_data = generate_initial_data()
    
    with open("initial_data.json", "w") as f:
        json.dump(initial_data, f, indent=2)
    
    print(f"Generated {len(initial_data)} data points and saved to initial_data.json")
