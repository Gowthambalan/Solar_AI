import json
import os
from typing import List, Dict, Any, Tuple

from app.config.constants import CLEANED_DIR, OUTPUT_DIR



# anomaly detection and data cleaning for inverter JSON records

class InverterDataProcessor:
    def __init__(self, anomaly_log_path="anomalies_log.txt"):
        self.prev_record: Dict[str, Any] = {}
        self.seen: set[Tuple[str, str]] = set()
        self.anomaly_log_path = anomaly_log_path

    def log_anomalies(self, record_id: str, anomalies: List[str]):
        """Write anomalies to a log file instead of embedding them in JSON."""
        if not anomalies:
            return
        with open(self.anomaly_log_path, "a", encoding="utf-8") as log_file:
            for msg in anomalies:
                log_file.write(f"{record_id} - {msg}\n")

    def remove_duplicate_or_invalid(self, record: Dict[str, Any]) -> bool:
        """Skip duplicates or invalid readings."""
        reading_id = record["properties"].get("readingId", {}).get("value")
        inverter_id = record["properties"].get("asset", {}).get("properties", {}).get("inverterId", {}).get("value")
        timestamp = record["properties"].get("timestamp", {}).get("value")

        if not reading_id or not inverter_id or not timestamp:
            self.log_anomalies(inverter_id or "UNKNOWN", ["Invalid reading: missing readingId, inverterId, or timestamp"])
            return False

        key = (reading_id, timestamp)
        if key in self.seen:
            self.log_anomalies(reading_id, ["Duplicate reading, skipped"])
            return False

        self.seen.add(key)
        return True

    def get_value(self, record, path: List[str]):
        """Safely extract nested value."""
        node = record
        for key in path:
            node = node.get("properties", {}).get(key, {})
        return node.get("value")

    def set_value(self, record, path: List[str], value):
        """Safely set nested value."""
        node = record
        for key in path[:-1]:
            node = node.get("properties", {}).get(key, {})
        last = path[-1]
        if "properties" in node and last in node["properties"]:
            node["properties"][last]["value"] = value

    def process_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply range validation and log anomalies externally."""
        if not self.remove_duplicate_or_invalid(record):
            return record  # invalid/duplicate are not added further

        anomalies = []
        validation_rules = {
            "power": {
                "acActive": (0, 10000),
                "acReactive": (-5000, 5000),
                "powerFactor": (0.9, 1.05),
            },
            "electrical": {
                "acVoltage": (215, 245),
                "acCurrent": (0, 20),
                "frequency": (49.0, 51.0),
            },
            "energy": {
                "today": (0, 200),
                "lifetime": (0, 100000),
            },
            "thermal": {
                "inverterTemp1": (-20, 80),
                "ambientTemp": (-10, 60),
            },
            "runtime": {
                "todayHours": (0, 24),
            },
            "safety": {
                "insulationResistance": (100, 100000),
                "groundLeakageCurrent": (0, 100),
            },
        }

        def validate(section, key, current, prev):
            if section not in validation_rules or key not in validation_rules[section]:
                return current
            min_val, max_val = validation_rules[section][key]
            if current is None or not (min_val <= current <= max_val):
                anomalies.append(
                    f"{section}.{key} value {current} out of range [{min_val}, {max_val}], replaced with previous {prev}"
                )
                return prev
            return current

        def get_prev_value(path: List[str], default):
            node = self.prev_record
            for key in path:
                node = node.get("properties", {}).get(key, {})
            return node.get("value", default)

        # Apply all section rules
        for section, keys in validation_rules.items():
            for key in keys.keys():
                path = [section, key]
                current = self.get_value(record, path)
                prev = get_prev_value(path, current)
                validated = validate(section, key, current, prev)
                self.set_value(record, path, validated)

        # Log anomalies externally
        reading_id = record["properties"].get("readingId", {}).get("value") or \
                     record["properties"].get("asset", {}).get("properties", {}).get("inverterId", {}).get("value") or \
                     "UNKNOWN"
        self.log_anomalies(reading_id, anomalies)

        # Remove anomalies from output
        record.pop("anomalies", None)
        record.pop("anomalyFlag", None)

        self.prev_record = record
        return record

    def process_stream(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.process_record(r) for r in records]


def process_bulk_json_folder(input_folder: str, output_folder: str):
    processor = InverterDataProcessor()
    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if not file_name.endswith(".json"):
            continue

        input_path = os.path.join(input_folder, file_name)
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f" Error reading {file_name}: {e}")
            continue

        if isinstance(data, dict):
            data = [data]

        cleaned_data = processor.process_stream(data)
        output_path = os.path.join(output_folder, f"cleaned_{file_name}")

        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(cleaned_data, out_f, indent=2)

        print(f" Processed {file_name}  {output_path}")


# ---------- Usage ----------
input_folder = OUTPUT_DIR
output_folder = CLEANED_DIR

process_bulk_json_folder(input_folder, output_folder)
 