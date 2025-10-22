import json
import os
from pymongo import MongoClient, ASCENDING, errors
from app.config.constants import CLEANED_DIR, MONGO_URI,DB_NAME,COLLECTION_NAME

# ----------------- MongoDB Connection -----------------
MONGO_URI = MONGO_URI
DB_NAME = DB_NAME
COLLECTION_NAME = COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Ensure unique index on readingId + timestamp
collection.create_index([("readingId", ASCENDING), ("timestamp", ASCENDING)], unique=True)

# ----------------- Extract helper -----------------
def extract_value(record, path):
    """Safely extract nested value from properties"""
    node = record.get("properties", {})
    for key in path:
        node = node.get(key, {})
        if "properties" in node:
            node = node["properties"]
    return node.get("value")

# ----------------- Function to insert JSON data -----------------
def insert_json_to_mongo(json_data):
    inserted_count = 0
    for record in json_data:
        try:
            # Extract important fields from nested structure
            reading_id = extract_value(record, ["readingId"])
            timestamp = extract_value(record, ["timestamp"])
            inverter_id = extract_value(record, ["asset", "inverterId"]) or \
                          extract_value(record, ["asset", "properties", "inverterId"])

            if not reading_id or not timestamp:
                print("⚠️ Skipping record: Missing readingId or timestamp")
                continue

            # Create a flattened summary for quick lookup
            doc = {
                "readingId": reading_id,
                "timestamp": timestamp,
                "inverterId": inverter_id,
                "siteId": extract_value(record, ["asset", "siteId"]),
                "plantId": extract_value(record, ["asset", "plantId"]),
                "power_acActive": extract_value(record, ["power", "acActive"]),
                "power_acReactive": extract_value(record, ["power", "acReactive"]),
                "electrical_acVoltage": extract_value(record, ["electrical", "acVoltage"]),
                "electrical_acCurrent": extract_value(record, ["electrical", "acCurrent"]),
                "temperature": extract_value(record, ["thermal", "inverterTemp1"]),
                "frequency": extract_value(record, ["electrical", "frequency"]),
                # Store full record as raw JSON
                "raw_document": record
            }

            # Insert with duplicate handling
            collection.insert_one(doc)
            inserted_count += 1

        except errors.DuplicateKeyError:
            print(f"Duplicate skipped: readingId={reading_id}, timestamp={timestamp}")
        except Exception as e:
            print(f" Error inserting record: {e}")

    return inserted_count

# ----------------- Bulk insert from folder -----------------
def insert_bulk_json_folder(folder_path):
    total_inserted = 0
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                elif not isinstance(data, list):
                    print(f"Skipping {file_name}: invalid JSON format")
                    continue

                inserted = insert_json_to_mongo(data)
                total_inserted += inserted
                print(f" {file_name}: inserted {inserted} records")

            except Exception as e:
                print(f" Error reading {file_name}: {e}")

    print(f" Total inserted records: {total_inserted}")

# ----------------- Usage -----------------
json_folder = CLEANED_DIR  # Replace with your cleaned JSON folder
insert_bulk_json_folder(json_folder)
 