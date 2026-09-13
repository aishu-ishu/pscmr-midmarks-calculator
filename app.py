import os
import gc
import io
import math
import cv2
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import numpy as np
from PIL import Image
import pytesseract

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
        "Mid1_Score": mid1_total,
        "Mid2_Score": mid2_total,
        "Best_Mid_80": best_80,
        "Other_Mid_20": other_20,
        "Final_Mid_Average": final_mid_avg,
        "Required_Sem_Marks": req_sem,
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process-image", methods=["POST"])
def process_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        image_bytes = file.read()
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = np.array(pil_img)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))

        h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

        table_grid = cv2.add(h_lines, v_lines)

        contours, _ = cv2.findContours(
            table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w > 20 and h > 12 and w < img.shape[1] * 0.9:
                boxes.append((x, y, w, h))

        if not boxes:
            return jsonify({"error": "Could not detect table grid lines"}), 400

        boxes = sorted(boxes, key=lambda b: b[1])

        row_threshold = 12
        grid_rows = []
        for box in boxes:
            placed = False
            for r in grid_rows:
                avg_y = sum(b[1] for b in r) / len(r)
                if abs(box[1] - avg_y) < row_threshold:
                    r.append(box)
                    placed = True
                    break
            if not placed:
                grid_rows.append([box])

        for r in grid_rows:
            r.sort(key=lambda b: b[0])

        extracted_grid = []
        for r in grid_rows:
            row_texts = []
            for x, y, w, h in r:
                cell_crop = img[y + 2 : y + h - 2, x + 2 : x + w - 2]
                if cell_crop.size == 0:
                    row_texts.append("")
                    continue
                cell_pil = Image.fromarray(cell_crop)
                cell_text = pytesseract.image_to_string(cell_pil, config="--psm 7").strip()
                row_texts.append(cell_text)
            extracted_grid.append(row_texts)

        header_row = extracted_grid[0]
        subjects = [
            s for s in header_row if s.lower() not in ["subject", "total", ""]
        ]

        target_columns = [
            "Unit-1",
            "Unit-2",
            "Unit-3(1)",
            "Obj-1(A)",
            "Assignment-1(A)",
            "Internal-I total",
        ]

        metric_map = {
            "unit-1": "Unit-1",
            "unit-2": "Unit-2",
            "unit-3(1)": "Unit-3(1)",
            "unit-3": "Unit-3(1)",
            "obj-1(a)": "Obj-1(A)",
            "obj-i(a)": "Obj-1(A)",
            "assignment-1(a)": "Assignment-1(A)",
            "assignment-i(a)": "Assignment-1(A)",
            "internal-i total": "Internal-I total",
        }

        subject_data = {s: {col: None for col in target_columns} for s in subjects}

        for r_idx in range(1, len(extracted_grid)):
            row = extracted_grid[r_idx]
            if not row:
                continue

            raw_label = row[0].lower().strip()
            matched_key = None
            for k, v in metric_map.items():
                if k in raw_label:
                    matched_key = v
                    break
            if not matched_key:
                continue

            for s_idx, subject in enumerate(subjects):
                col_idx = s_idx + 1
                if col_idx < len(row):
                    cell_val = row[col_idx].replace(" ", "")
                    if cell_val and cell_val not in ["-", "--", "None", "null"]:
                        subject_data[subject][matched_key] = cell_val

        final_rows = []
        for s in subjects:
            s_dict = {"Subject": s}
            s_dict.update(subject_data[s])

            analytics = calculate_analytics(
                u1=s_dict["Unit-1"],
                u2=s_dict["Unit-2"],
                u3=s_dict["Unit-3(1)"],
                obj=s_dict["Obj-1(A)"],
                assign=s_dict["Assignment-1(A)"],
            )

            s_dict.update(analytics)
            final_rows.append(s_dict)

        gc.collect()
        return jsonify({"rows": final_rows})

    except Exception as e:
        gc.collect()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
