import os
import json
import yaml
import logging
from config.constants import CANONICAL_PATH, OUTPUT_DIR
from app.llm.model_loader import load_llm_chain

logger = logging.getLogger(__name__)

def process_files(files):
    """Process multiple uploaded JSON files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CANONICAL_PATH, "r") as f:
        canonical_schema = yaml.safe_load(f)

    chain = load_llm_chain()
    results = []

    for file in files:
        try:
            vendor_data = json.load(file.file)
            canonical_output = chain.invoke({
                "schema": json.dumps(canonical_schema, indent=2),
                "input_json": json.dumps(vendor_data, indent=2)
            })

            output_path = os.path.join(OUTPUT_DIR, file.filename)
            with open(output_path, "w") as out_f:
                json.dump(canonical_output, out_f, indent=2)

            results.append({"file": file.filename, "status": "success"})
        except Exception as e:
            results.append({"file": file.filename, "status": "failed", "error": str(e)})
    return results


