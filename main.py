from prometheus_client import start_http_server, Gauge
import os
import requests
from dotenv import load_dotenv
import time

# Load env vars
load_dotenv()
API_URL = os.getenv("API_URL")

if not API_URL:
    raise ValueError("API URL not found in .env file")

# Prometheus metrics
record_count_gauge = Gauge('green_buildings_record_count', 'Total number of green building records')
certified_total_gauge = Gauge('green_buildings_certified_total', 'Number of certified green buildings')
certified_by_stage_gauge = Gauge('green_buildings_certified_by_stage', 'Certified buildings by stage', ['stage'])
certified_by_energy_gauge = Gauge('green_buildings_certified_by_energy', 'Certified buildings by energy rating', ['rating'])

def fetch_data():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        records = data['result']['records']
        count = len(records)
        record_count_gauge.set(count)

        certified_by_stage_gauge.clear()
        certified_by_energy_gauge.clear()

        certified_total = 0
        stage_counts = {}
        energy_counts = {}

        for record in records:
            has_cert = any(record.get(f'certificate_score_{x}') not in [None, '', 'NaN'] for x in ['a', 'b', 'pre'])
            if has_cert:
                certified_total += 1

            stage = record.get('certification_status')
            if stage:
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

            for x in ['a', 'b', 'pre']:
                energy = record.get(f'certificate_energy_{x}')
                if energy and energy != 'NaN':
                    energy_counts[energy] = energy_counts.get(energy, 0) + 1

        certified_total_gauge.set(certified_total)

        for stage, count in stage_counts.items():
            certified_by_stage_gauge.labels(stage=stage).set(count)

        for rating, count in energy_counts.items():
            certified_by_energy_gauge.labels(rating=rating).set(count)

        print(f'Fetched {count} records. Certified: {certified_total}')
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == '__main__':
    start_http_server(8000) 
    while True:
        fetch_data()
        time.sleep(30)
