from flask import Flask, request, jsonify
import pandas as pd
import json
import re
import tempfile
import os
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
STANDARD_FIELDS = ["task_name", "description", "assignee", "start_date", "end_date", "priority", "status"]

# Configure Google Generative AI
configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)

@app.route("/transform_excel", methods=["POST"])
def transform_excel():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Load Excel file
        sheets_dict = pd.read_excel(tmp_path, sheet_name=None)
        all_rows = []

        for sheet_name, df in sheets_dict.items():
            df = df.where(pd.notna(df), None)
            sheet_rows = df.to_dict(orient="records")
            for row in sheet_rows:
                row["_sheet"] = sheet_name
            all_rows.extend(sheet_rows)

        # Compose the prompt
        prompt = f"""
        You are a data transformation assistant for a project management tool.

        Given this list of task rows extracted from an Excel workbook (including multiple sheets): {all_rows}

        1. Analyze and detect the correct hierarchy:
           * Either project → phases → tasks
           * Or project → modules → phases → tasks

        2. Create a JSON structure: 
        {{
            "project_name": "<inferred or 'Imported Project'>",
            "modules": {{
                "Module A": {{
                    "Phase 1": [
                        {{
                            "task_name": "...",
                            "mapped_fields": {{
                                "standard_field_1": "value"
                            }},
                            "custom_fields": {{
                                "unmatched_field_1": "value"
                            }}
                        }}
                    ]
                }}
            }}
        }}

        3. Use this list of standard fields to match task fields: {STANDARD_FIELDS}

        4. Any fields not matching standard ones should go into `custom_fields`.

        Return only valid JSON without any explanations or markdown formatting.
        """

        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean and parse the response
        response_cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', response_text).strip()
        parsed_json = json.loads(response_cleaned)

        return jsonify(parsed_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    app.run(debug=True)
