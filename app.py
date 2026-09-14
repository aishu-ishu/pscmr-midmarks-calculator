import os
import gc
import math
import re
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

def parse_score(val):
    if not val or val in ["-", "--", "null", "None", ""]:
        return 0.0
    if isinstance(val, str) and "/" in val:
        try:
            return float(val.split("/")[0])
        except ValueError:
            return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0

def round_half_up(n):
    return math.floor(n + 0.5)

def calculate_analytics(
    u1, u2, u3, obj, assign, mid2_u1=0, mid2_u2=0, mid2_u3=0, mid2_obj=0, mid2_assign=0
):
    m1_units = round_half_up(
        (parse_score(u1) + parse_score(u2) + parse_score(u3)) / 2.0
    )
    mid1_total = int(m1_units + parse_score(obj) + parse_score(assign))

    m2_units = round_half_up(
        (parse_score(mid2_u1) + parse_score(mid2_u2) + parse_score(mid2_u3)) / 2.0
    )
    mid2_total = int(m2_units + parse_score(mid2_obj) + parse_score(mid2_assign))

    best_mid = max(mid1_total, mid2_total)
    other_mid = min(mid1_total, mid2_total)

    best_80 = int(round_half_up(best_mid * 0.8))
    other_20 = int(round_half_up(other_mid * 0.2)) if mid2_total > 0 else 0

    final_mid_avg = best_80 + other_20
    req_sem = max(24, 40 - final_mid_avg)

    return {
        "Mid1_Score": min(30, mid1_total),
        "Mid2_Score": min(30, mid2_total),
        "Best_Mid_80": min(30, best_80),
        "Other_Mid_20": min(30, other_20),
        "Final_Mid_Average": min(30, final_mid_avg),
        "Required_Sem_Marks": req_sem,
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/parse-text", methods=["POST"])
def parse_text():
    data = request.get_json()
    extracted_text = data.get("extracted_text", "")
    
    if not extracted_text:
        return jsonify({"error": "No text received"}), 400

    try:
        lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
        
        # Extract all numbers from the client-side text output
        numbers = []
        for line in lines:
            found = re.findall(r'\b\d+(?:\.\d+)?\b', line)
            if found:
                numbers.extend([float(n) for n in found])

        # Filter realistic mark values (0 to 30 range)
        valid_marks = [n for n in numbers if 0 <= n <= 30]

        u1 = valid_marks[0] if len(valid_marks) > 0 else 10
        u2 = valid_marks[1] if len(valid_marks) > 1 else 10
        u3 = valid_marks[2] if len(valid_marks) > 2 else 10
        obj = valid_marks[3] if len(valid_marks) > 3 else 4
        assign = valid_marks[4] if len(valid_marks) > 4 else 4

        analytics = calculate_analytics(u1=u1, u2=u2, u3=u3, obj=obj, assign=assign)

        final_rows = [{
            "Subject": "Parsed Subject",
            **analytics
        }]

        gc.collect()
        return jsonify({"rows": final_rows})

    except Exception as e:
        gc.collect()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
