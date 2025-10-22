# import os
# import json
# import asyncio
# import yaml
# import logging
# from app.config.constants import CANONICAL_PATH, OUTPUT_DIR, LOG_FILE
# from app.llm.model_loader import load_llm_chain

# logger = logging.getLogger(__name__)

# # file processing service

# async def process_files(files):
#     """Process multiple uploaded JSON files."""
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
#     os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

#     with open(CANONICAL_PATH, "r") as f:
#         canonical_schema = yaml.safe_load(f)

#     chain = load_llm_chain()
#     results = []

#     for file in files:
#         try:
#             content = await file.read()
#             vendor_data = json.loads(content)
            
#             canonical_output = chain.invoke({
#                 "schema": json.dumps(canonical_schema, indent=2),
#                 "input_json": json.dumps(vendor_data, indent=2)
#             })

#             output_path = os.path.join(OUTPUT_DIR, f"transformed_{file.filename}")
#             with open(output_path, "w") as out_f:
#                 json.dump(canonical_output, out_f, indent=2)

#             results.append({"file": file.filename, "status": "success", "output_file": output_path})
#         except Exception as e:
#             logger.error(f"Error processing {file.filename}: {str(e)}")
#             results.append({"file": file.filename, "status": "failed", "error": str(e)})
#         finally:
#             await file.close()


import os
import json
import yaml
import logging
from app.config.constants import CANONICAL_PATH, OUTPUT_DIR
from app.llm.model_loader import load_llm_chain

logger = logging.getLogger(__name__)

def process_files(files):
    """Process multiple uploaded JSON files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load canonical schema
    with open(CANONICAL_PATH, "r") as f:
        canonical_schema = yaml.safe_load(f)

    # Load LLM chain
    chain = load_llm_chain()
    results = []

    for file in files:
        try:
            # Read JSON from uploaded file
            vendor_data = json.load(file.file)

            # Run LLM chain
            canonical_output = chain.invoke({
                "schema": json.dumps(canonical_schema, indent=2),
                "input_json": json.dumps(vendor_data, indent=2)
            })

            # Save output JSON
            output_path = os.path.join(OUTPUT_DIR, file.filename)
            with open(output_path, "w") as out_f:
                json.dump(canonical_output, out_f, indent=2)

            results.append({"file": file.filename, "status": "success"})
            logger.info(f"Processed file: {file.filename}")
        except Exception as e:
            results.append({"file": file.filename, "status": "failed", "error": str(e)})
            logger.error(f"Failed file: {file.filename} - {str(e)}")

    return results
