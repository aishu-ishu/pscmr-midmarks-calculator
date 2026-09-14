# import os
# import gc
# import io
# import math
# import cv2
# from flask import Flask, jsonify, render_template, request
# from flask_cors import CORS
# import numpy as np
# from PIL import Image
# import pytesseract

# app = Flask(__name__)
# CORS(app)

# app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# def parse_score(val):
#     if not val or val in ["-", "--", "null", "None", "", "."]:
#         return 0.0
#     if isinstance(val, str) and "/" in val:
#         try:
#             return float(val.split("/")[0])
#         except ValueError:
#             return 0.0
#     try:
#         return float(val)
#     except ValueError:
#         return 0.0

# def round_half_up(n):
#     return math.floor(n + 0.5)

# def calculate_analytics(
#     u1, u2, u3, obj, assign, mid2_u1=0, mid2_u2=0, mid2_u3=0, mid2_obj=0, mid2_assign=0
# ):
#     m1_units_sum = parse_score(u1) + parse_score(u2) + parse_score(u3)
#     m1_units = round_half_up(m1_units_sum / 2.0)
#     mid1_total = int(m1_units + parse_score(obj) + parse_score(assign))

#     m2_units_sum = parse_score(mid2_u1) + parse_score(mid2_u2) + parse_score(mid2_u3)
#     m2_units = round_half_up(m2_units_sum / 2.0)
#     mid2_total = int(m2_units + parse_score(mid2_obj) + parse_score(mid2_assign))

#     best_mid = max(mid1_total, mid2_total)
#     other_mid = min(mid1_total, mid2_total)

#     best_80 = int(round_half_up(best_mid * 0.8))
#     other_20 = int(round_half_up(other_mid * 0.2)) if (mid1_total > 0 or mid2_total > 0) else 0

#     final_mid_avg = best_80 + other_20
#     req_sem = max(24, 40 - final_mid_avg)

#     return {
#         "Mid1_Score": mid1_total,
#         "Mid2_Score": mid2_total,
#         "Best_Mid_80": best_80,
#         "Other_Mid_20": other_20,
#         "Final_Mid_Average": final_mid_avg,
#         "Required_Sem_Marks": req_sem,
#     }

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/process-image", methods=["POST"])
# def process_image():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400

#     try:
#         image_bytes = file.read()
#         pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
#         max_width = 1200
#         if pil_img.width > max_width:
#             ratio = max_width / float(pil_img.width)
#             new_height = int(float(pil_img.height) * ratio)
#             pil_img = pil_img.resize((max_width, new_height), Image.Resampling.LANCZOS)

#         img = np.array(pil_img)
#         gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

#         thresh = cv2.threshold(
#             gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
#         )[1]

#         h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
#         v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))

#         h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
#         v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

#         table_grid = cv2.add(h_lines, v_lines)

#         contours, _ = cv2.findContours(
#             table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
#         )

#         boxes = []
#         for c in contours:
#             x, y, w, h = cv2.boundingRect(c)
#             if w > 20 and h > 12 and w < img.shape[1] * 0.9:
#                 boxes.append((x, y, w, h))

#         if not boxes:
#             return jsonify({"error": "Could not detect table grid lines"}), 400

#         boxes = sorted(boxes, key=lambda b: b[1])

#         row_threshold = 12
#         grid_rows = []
#         for box in boxes:
#             placed = False
#             for r in grid_rows:
#                 avg_y = sum(b[1] for b in r) / len(r)
#                 if abs(box[1] - avg_y) < row_threshold:
#                     r.append(box)
#                     placed = True
#                     break
#             if not placed:
#                 grid_rows.append([box])

#         for r in grid_rows:
#             r.sort(key=lambda b: b[0])

#         extracted_grid = []
#         for r in grid_rows:
#             row_texts = []
#             for x, y, w, h in r:
#                 cell_crop = img[y + 2 : y + h - 2, x + 2 : x + w - 2]
#                 if cell_crop.size == 0:
#                     row_texts.append("")
#                     continue
#                 cell_pil = Image.fromarray(cell_crop)
                
#                 cell_text = pytesseract.image_to_string(
#                     cell_pil, config="--oem 1 --psm 7"
#                 ).strip()
#                 row_texts.append(cell_text)
#             extracted_grid.append(row_texts)

#         header_row = extracted_grid[0]
        
#         subjects = []
#         subject_col_indices = []
#         for idx, text in enumerate(header_row):
#             cleaned = text.strip()
#             if idx > 0 and cleaned.lower() not in ["subject", "total", ""] and len(cleaned) > 0:
#                 subjects.append(cleaned)
#                 subject_col_indices.append(idx)

#         if not subjects and len(extracted_grid) > 0:
#             num_cols = len(header_row)
#             for idx in range(1, num_cols):
#                 subjects.append(header_row[idx] if header_row[idx] else f"Subject_{idx}")
#                 subject_col_indices.append(idx)

#         target_columns = [
#             "Unit-1", "Unit-2", "Unit-3(1)", "Obj-1(A)", "Assignment-1(A)", "Internal-I total",
#             "Unit-3(2)", "Unit-4", "Unit-5", "Obj-2(A)", "Assignment-2(A)", "Internal-II total"
#         ]

#         # Prioritize specific sub-keys (like unit-3(2)) before generic substrings (like unit-3)
#         metric_map = {
#             "unit-3(2)": "Unit-3(2)",
#             "unit-3.2": "Unit-3(2)",
#             "unit-3 (2)": "Unit-3(2)",
#             "unit-3(1)": "Unit-3(1)",
#             "unit-3.1": "Unit-3(1)",
#             "unit-3": "Unit-3(1)",
#             "unit-1": "Unit-1",
#             "unit-2": "Unit-2",
#             "obj-1(a)": "Obj-1(A)",
#             "obj-i(a)": "Obj-1(A)",
#             "assignment-1(a)": "Assignment-1(A)",
#             "assignment-i(a)": "Assignment-1(A)",
#             "internal-i total": "Internal-I total",
#             "unit-4": "Unit-4",
#             "unit-5": "Unit-5",
#             "obj-2(a)": "Obj-2(A)",
#             "assignment-2(a)": "Assignment-2(A)",
#             "internal-ii total": "Internal-II total",
#         }

#         subject_data = {s: {col: None for col in target_columns} for s in subjects}

#         for r_idx in range(1, len(extracted_grid)):
#             row = extracted_grid[r_idx]
#             if not row:
#                 continue

#             raw_label = row[0].lower().strip()
#             matched_key = None
            
#             for k, v in metric_map.items():
#                 if k in raw_label:
#                     matched_key = v
#                     break
            
#             # Fallback based on structural row position if OCR label is unreadable
#             if not matched_key and 0 < r_idx <= len(target_columns):
#                 matched_key = target_columns[r_idx - 1]

#             if not matched_key:
#                 continue

#             for s_idx, subject in enumerate(subjects):
#                 col_idx = subject_col_indices[s_idx] if s_idx < len(subject_col_indices) else (s_idx + 1)
#                 if col_idx < len(row):
#                     cell_val = row[col_idx].replace(" ", "")
#                     if cell_val and cell_val not in ["-", "--", "None", "null", "."]:
#                         subject_data[subject][matched_key] = cell_val

#         final_rows = []
#         for s in subjects:
#             s_dict = {"Subject": s}
#             s_dict.update(subject_data[s])

#             analytics = calculate_analytics(
#                 u1=s_dict["Unit-1"],
#                 u2=s_dict["Unit-2"],
#                 u3=s_dict["Unit-3(1)"],
#                 obj=s_dict["Obj-1(A)"],
#                 assign=s_dict["Assignment-1(A)"],
#                 mid2_u1=s_dict["Unit-3(2)"],
#                 mid2_u2=s_dict["Unit-4"],
#                 mid2_u3=s_dict["Unit-5"],
#                 mid2_obj=s_dict["Obj-2(A)"],
#                 mid2_assign=s_dict["Assignment-2(A)"],
#             )

#             s_dict.update(analytics)
#             final_rows.append(s_dict)

#         gc.collect()
#         return jsonify({"rows": final_rows})

#     except Exception as e:
#         gc.collect()
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=False)
import os
import gc
import io
import math
import cv2
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import numpy as np
from PIL import Image
import requests

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Pull API key securely from environment variables
OCR_API_KEY = os.environ.get("OCR_API_KEY")

def parse_score(val):
    if not val or val in ["-", "--", "null", "None", "", "."]:
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
    m1_units_sum = parse_score(u1) + parse_score(u2) + parse_score(u3)
    m1_units = round_half_up(m1_units_sum / 2.0)
    mid1_total = int(m1_units + parse_score(obj) + parse_score(assign))

    m2_units_sum = parse_score(mid2_u1) + parse_score(mid2_u2) + parse_score(mid2_u3)
    m2_units = round_half_up(m2_units_sum / 2.0)
    mid2_total = int(m2_units + parse_score(mid2_obj) + parse_score(mid2_assign))

    best_mid = max(mid1_total, mid2_total)
    other_mid = min(mid1_total, mid2_total)

    best_80 = int(round_half_up(best_mid * 0.8))
    other_20 = int(round_half_up(other_mid * 0.2)) if (mid1_total > 0 or mid2_total > 0) else 0

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

def ocr_crop_with_api(cell_crop):
    """Sends individual OpenCV cell crops to OCR.space API instead of local pytesseract"""
    if not OCR_API_KEY or cell_crop.size == 0:
        return ""
    try:
        success, encoded_image = cv2.imencode('.png', cell_crop)
        if not success:
            return ""
        
        cell_bytes = encoded_image.tobytes()
        
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("cell.png", cell_bytes, "image/png")},
            data={
                "apikey": OCR_API_KEY,
                "language": "eng",
                "isTable": False,
                "scale": True
            },
            timeout=10
        )
        
        result = response.json()
        if result.get("IsErroredOnProcessing"):
            return ""
            
        parsed_results = result.get("ParsedResults", [])
        if parsed_results:
            return parsed_results[0].get("ParsedText", "").strip()
    except Exception:
        pass
    return ""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process-image", methods=["POST"])
def process_image():
    if not OCR_API_KEY:
        return jsonify({"error": "OCR_API_KEY environment variable not configured on server"}), 500

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        image_bytes = file.read()
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        max_width = 1200
        if pil_img.width > max_width:
            ratio = max_width / float(pil_img.width)
            new_height = int(float(pil_img.height) * ratio)
            pil_img = pil_img.resize((max_width, new_height), Image.Resampling.LANCZOS)

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
                
                # Using the OCR.space wrapper function for each cell crop
                cell_text = ocr_crop_with_api(cell_crop)
                row_texts.append(cell_text)
            extracted_grid.append(row_texts)

        if not extracted_grid:
            return jsonify({"error": "Failed to extract text from grid cells."}), 400

        header_row = extracted_grid[0]
        
        subjects = []
        subject_col_indices = []
        for idx, text in enumerate(header_row):
            cleaned = text.strip()
            if idx > 0 and cleaned.lower() not in ["subject", "total", ""] and len(cleaned) > 0:
                subjects.append(cleaned)
                subject_col_indices.append(idx)

        if not subjects and len(extracted_grid) > 0:
            num_cols = len(header_row)
            for idx in range(1, num_cols):
                subjects.append(header_row[idx] if header_row[idx] else f"Subject_{idx}")
                subject_col_indices.append(idx)

        target_columns = [
            "Unit-1", "Unit-2", "Unit-3(1)", "Obj-1(A)", "Assignment-1(A)", "Internal-I total",
            "Unit-3(2)", "Unit-4", "Unit-5", "Obj-2(A)", "Assignment-2(A)", "Internal-II total"
        ]

        metric_map = {
            "unit-3(2)": "Unit-3(2)",
            "unit-3.2": "Unit-3(2)",
            "unit-3 (2)": "Unit-3(2)",
            "unit-3(1)": "Unit-3(1)",
            "unit-3.1": "Unit-3(1)",
            "unit-3": "Unit-3(1)",
            "unit-1": "Unit-1",
            "unit-2": "Unit-2",
            "obj-1(a)": "Obj-1(A)",
            "obj-i(a)": "Obj-1(A)",
            "assignment-1(a)": "Assignment-1(A)",
            "assignment-i(a)": "Assignment-1(A)",
            "internal-i total": "Internal-I total",
            "unit-4": "Unit-4",
            "unit-5": "Unit-5",
            "obj-2(a)": "Obj-2(A)",
            "assignment-2(a)": "Assignment-2(A)",
            "internal-ii total": "Internal-II total",
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
            
            if not matched_key and 0 < r_idx <= len(target_columns):
                matched_key = target_columns[r_idx - 1]

            if not matched_key:
                continue

            for s_idx, subject in enumerate(subjects):
                col_idx = subject_col_indices[s_idx] if s_idx < len(subject_col_indices) else (s_idx + 1)
                if col_idx < len(row):
                    cell_val = row[col_idx].replace(" ", "")
                    if cell_val and cell_val not in ["-", "--", "None", "null", "."]:
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
                mid2_u1=s_dict["Unit-3(2)"],
                mid2_u2=s_dict["Unit-4"],
                mid2_u3=s_dict["Unit-5"],
                mid2_obj=s_dict["Obj-2(A)"],
                mid2_assign=s_dict["Assignment-2(A)"],
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
