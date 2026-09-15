# # # import os
# # # import gc
# # # import io
# # # import math
# # # import cv2
# # # from flask import Flask, jsonify, render_template, request
# # # from flask_cors import CORS
# # # import numpy as np
# # # from PIL import Image
# # # import pytesseract

# # # app = Flask(__name__)
# # # CORS(app)

# # # app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# # # def parse_score(val):
# # #     if not val or val in ["-", "--", "null", "None", "", "."]:
# # #         return 0.0
# # #     if isinstance(val, str) and "/" in val:
# # #         try:
# # #             return float(val.split("/")[0])
# # #         except ValueError:
# # #             return 0.0
# # #     try:
# # #         return float(val)
# # #     except ValueError:
# # #         return 0.0

# # # def round_half_up(n):
# # #     return math.floor(n + 0.5)

# # # def calculate_analytics(
# # #     u1, u2, u3, obj, assign, mid2_u1=0, mid2_u2=0, mid2_u3=0, mid2_obj=0, mid2_assign=0
# # # ):
# # #     m1_units_sum = parse_score(u1) + parse_score(u2) + parse_score(u3)
# # #     m1_units = round_half_up(m1_units_sum / 2.0)
# # #     mid1_total = int(m1_units + parse_score(obj) + parse_score(assign))

# # #     m2_units_sum = parse_score(mid2_u1) + parse_score(mid2_u2) + parse_score(mid2_u3)
# # #     m2_units = round_half_up(m2_units_sum / 2.0)
# # #     mid2_total = int(m2_units + parse_score(mid2_obj) + parse_score(mid2_assign))

# # #     best_mid = max(mid1_total, mid2_total)
# # #     other_mid = min(mid1_total, mid2_total)

# # #     best_80 = int(round_half_up(best_mid * 0.8))
# # #     other_20 = int(round_half_up(other_mid * 0.2)) if (mid1_total > 0 or mid2_total > 0) else 0

# # #     final_mid_avg = best_80 + other_20
# # #     req_sem = max(24, 40 - final_mid_avg)

# # #     return {
# # #         "Mid1_Score": mid1_total,
# # #         "Mid2_Score": mid2_total,
# # #         "Best_Mid_80": best_80,
# # #         "Other_Mid_20": other_20,
# # #         "Final_Mid_Average": final_mid_avg,
# # #         "Required_Sem_Marks": req_sem,
# # #     }

# # # @app.route("/")
# # # def home():
# # #     return render_template("index.html")

# # # @app.route("/guide")
# # # def guide_page():
# # #     return render_template("bs.html")

# # # @app.route("/process-image", methods=["POST"])
# # # def process_image():
# # #     if "file" not in request.files:
# # #         return jsonify({"error": "No file uploaded"}), 400

# # #     file = request.files["file"]
# # #     if file.filename == "":
# # #         return jsonify({"error": "No selected file"}), 400

# # #     try:
# # #         image_bytes = file.read()
# # #         pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
# # #         max_width = 1200
# # #         if pil_img.width > max_width:
# # #             ratio = max_width / float(pil_img.width)
# # #             new_height = int(float(pil_img.height) * ratio)
# # #             pil_img = pil_img.resize((max_width, new_height), Image.Resampling.LANCZOS)

# # #         img = np.array(pil_img)
# # #         gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

# # #         thresh = cv2.threshold(
# # #             gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
# # #         )[1]

# # #         h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
# # #         v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))

# # #         h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
# # #         v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

# # #         table_grid = cv2.add(h_lines, v_lines)

# # #         contours, _ = cv2.findContours(
# # #             table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
# # #         )

# # #         boxes = []
# # #         for c in contours:
# # #             x, y, w, h = cv2.boundingRect(c)
# # #             if w > 20 and h > 12 and w < img.shape[1] * 0.9:
# # #                 boxes.append((x, y, w, h))

# # #         if not boxes:
# # #             return jsonify({"error": "Could not detect table grid lines"}), 400

# # #         boxes = sorted(boxes, key=lambda b: b[1])

# # #         row_threshold = 12
# # #         grid_rows = []
# # #         for box in boxes:
# # #             placed = False
# # #             for r in grid_rows:
# # #                 avg_y = sum(b[1] for b in r) / len(r)
# # #                 if abs(box[1] - avg_y) < row_threshold:
# # #                     r.append(box)
# # #                     placed = True
# # #                     break
# # #             if not placed:
# # #                 grid_rows.append([box])

# # #         for r in grid_rows:
# # #             r.sort(key=lambda b: b[0])

# # #         extracted_grid = []
# # #         for r in grid_rows:
# # #             row_texts = []
# # #             for x, y, w, h in r:
# # #                 cell_crop = img[y + 2 : y + h - 2, x + 2 : x + w - 2]
# # #                 if cell_crop.size == 0:
# # #                     row_texts.append("")
# # #                     continue
# # #                 cell_pil = Image.fromarray(cell_crop)
                
# # #                 cell_text = pytesseract.image_to_string(
# # #                     cell_pil, config="--oem 1 --psm 7"
# # #                 ).strip()
# # #                 row_texts.append(cell_text)
# # #             extracted_grid.append(row_texts)

# # #         header_row = extracted_grid[0]
        
# # #         subjects = []
# # #         subject_col_indices = []
# # #         for idx, text in enumerate(header_row):
# # #             cleaned = text.strip()
# # #             if idx > 0 and cleaned.lower() not in ["subject", "total", ""] and len(cleaned) > 0:
# # #                 subjects.append(cleaned)
# # #                 subject_col_indices.append(idx)

# # #         if not subjects and len(extracted_grid) > 0:
# # #             num_cols = len(header_row)
# # #             for idx in range(1, num_cols):
# # #                 subjects.append(header_row[idx] if header_row[idx] else f"Subject_{idx}")
# # #                 subject_col_indices.append(idx)

# # #         target_columns = [
# # #             "Unit-1", "Unit-2", "Unit-3(1)", "Obj-1(A)", "Assignment-1(A)", "Internal-I total",
# # #             "Unit-3(2)", "Unit-4", "Unit-5", "Obj-2(A)", "Assignment-2(A)", "Internal-II total"
# # #         ]

# # #         # Prioritize specific sub-keys (like unit-3(2)) before generic substrings (like unit-3)
# # #         metric_map = {
# # #             "unit-3(2)": "Unit-3(2)",
# # #             "unit-3.2": "Unit-3(2)",
# # #             "unit-3 (2)": "Unit-3(2)",
# # #             "unit-3(1)": "Unit-3(1)",
# # #             "unit-3.1": "Unit-3(1)",
# # #             "unit-3": "Unit-3(1)",
# # #             "unit-1": "Unit-1",
# # #             "unit-2": "Unit-2",
# # #             "obj-1(a)": "Obj-1(A)",
# # #             "obj-i(a)": "Obj-1(A)",
# # #             "assignment-1(a)": "Assignment-1(A)",
# # #             "assignment-i(a)": "Assignment-1(A)",
# # #             "internal-i total": "Internal-I total",
# # #             "unit-4": "Unit-4",
# # #             "unit-5": "Unit-5",
# # #             "obj-2(a)": "Obj-2(A)",
# # #             "assignment-2(a)": "Assignment-2(A)",
# # #             "internal-ii total": "Internal-II total",
# # #         }

# # #         subject_data = {s: {col: None for col in target_columns} for s in subjects}

# # #         for r_idx in range(1, len(extracted_grid)):
# # #             row = extracted_grid[r_idx]
# # #             if not row:
# # #                 continue

# # #             raw_label = row[0].lower().strip()
# # #             matched_key = None
            
# # #             for k, v in metric_map.items():
# # #                 if k in raw_label:
# # #                     matched_key = v
# # #                     break
            
# # #             # Fallback based on structural row position if OCR label is unreadable
# # #             if not matched_key and 0 < r_idx <= len(target_columns):
# # #                 matched_key = target_columns[r_idx - 1]

# # #             if not matched_key:
# # #                 continue

# # #             for s_idx, subject in enumerate(subjects):
# # #                 col_idx = subject_col_indices[s_idx] if s_idx < len(subject_col_indices) else (s_idx + 1)
# # #                 if col_idx < len(row):
# # #                     cell_val = row[col_idx].replace(" ", "")
# # #                     if cell_val and cell_val not in ["-", "--", "None", "null", "."]:
# # #                         subject_data[subject][matched_key] = cell_val

# # #         final_rows = []
# # #         for s in subjects:
# # #             s_dict = {"Subject": s}
# # #             s_dict.update(subject_data[s])

# # #             analytics = calculate_analytics(
# # #                 u1=s_dict["Unit-1"],
# # #                 u2=s_dict["Unit-2"],
# # #                 u3=s_dict["Unit-3(1)"],
# # #                 obj=s_dict["Obj-1(A)"],
# # #                 assign=s_dict["Assignment-1(A)"],
# # #                 mid2_u1=s_dict["Unit-3(2)"],
# # #                 mid2_u2=s_dict["Unit-4"],
# # #                 mid2_u3=s_dict["Unit-5"],
# # #                 mid2_obj=s_dict["Obj-2(A)"],
# # #                 mid2_assign=s_dict["Assignment-2(A)"],
# # #             )

# # #             s_dict.update(analytics)
# # #             final_rows.append(s_dict)

# # #         gc.collect()
# # #         return jsonify({"rows": final_rows})

# # #     except Exception as e:
# # #         gc.collect()
# # #         return jsonify({"error": str(e)}), 500

# # # if __name__ == "__main__":
# # #     port = int(os.environ.get("PORT", 5000))
# # #     app.run(host="0.0.0.0", port=port, debug=False)

# # import os

# # # Must be set before any Tesseract subprocess is spawned. On a throttled
# # # / fractional-CPU host (e.g. Render free tier), Tesseract's default
# # # internal multi-threading just adds scheduling overhead with no real
# # # extra core to use -- forcing 1 thread is measurably faster there.
# # os.environ.setdefault("OMP_THREAD_LIMIT", "1")

# # import gc
# # import io
# # import math
# # import threading
# # import cv2
# # from flask import Flask, jsonify, render_template, request
# # from flask_cors import CORS
# # import numpy as np
# # from PIL import Image
# # import pytesseract
# # from pytesseract import Output

# # app = Flask(__name__)
# # CORS(app)

# # # Free-tier hosts give you a fraction of one CPU core, not real
# # # parallelism. Rather than let concurrent uploads fight over that sliver
# # # of CPU (which is what was causing the "stuck on loading" behavior),
# # # serialize OCR work: one job runs at a time, others wait their turn.
# # _ocr_lock = threading.Lock()

# # app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# # def parse_score(val):
# #     if not val or val in ["-", "--", "null", "None", "", "."]:
# #         return 0.0
# #     if isinstance(val, str) and "/" in val:
# #         try:
# #             return float(val.split("/")[0])
# #         except ValueError:
# #             return 0.0
# #     try:
# #         return float(val)
# #     except ValueError:
# #         return 0.0

# # def round_half_up(n):
# #     return math.floor(n + 0.5)

# # def calculate_analytics(
# #     u1, u2, u3, obj, assign, mid2_u1=0, mid2_u2=0, mid2_u3=0, mid2_obj=0, mid2_assign=0
# # ):
# #     m1_units_sum = parse_score(u1) + parse_score(u2) + parse_score(u3)
# #     m1_units = round_half_up(m1_units_sum / 2.0)
# #     mid1_total = int(m1_units + parse_score(obj) + parse_score(assign))

# #     m2_units_sum = parse_score(mid2_u1) + parse_score(mid2_u2) + parse_score(mid2_u3)
# #     m2_units = round_half_up(m2_units_sum / 2.0)
# #     mid2_total = int(m2_units + parse_score(mid2_obj) + parse_score(mid2_assign))

# #     best_mid = max(mid1_total, mid2_total)
# #     other_mid = min(mid1_total, mid2_total)

# #     best_80 = int(round_half_up(best_mid * 0.8))
# #     other_20 = int(round_half_up(other_mid * 0.2)) if (mid1_total > 0 or mid2_total > 0) else 0

# #     final_mid_avg = best_80 + other_20
# #     req_sem = max(24, 40 - final_mid_avg)

# #     return {
# #         "Mid1_Score": mid1_total,
# #         "Mid2_Score": mid2_total,
# #         "Best_Mid_80": best_80,
# #         "Other_Mid_20": other_20,
# #         "Final_Mid_Average": final_mid_avg,
# #         "Required_Sem_Marks": req_sem,
# #     }


# # def erase_grid_lines(gray, table_grid):
# #     """
# #     Paint over the detected table grid lines so Tesseract doesn't read
# #     them as stray characters (vertical borders get misread as '|', '*',
# #     etc. and corrupt neighboring words) -- this is what made a single
# #     whole-table OCR pass unreliable.
# #     """
# #     line_mask = cv2.dilate(table_grid, np.ones((3, 3), np.uint8), iterations=1)
# #     cleaned = gray.copy()
# #     cleaned[line_mask > 0] = 255
# #     return cleaned


# # INK_THRESHOLD = 40  # empirically: dash cells measure ~0-10, real marks ~150+


# # def ocr_grid_batch(cleaned_gray, thresh, grid_rows):
# #     """
# #     Run Tesseract once PER ROW (not once per cell, and not once for the
# #     whole table).

# #     - Per-cell is accurate but spawns a subprocess per cell -- the main
# #       source of slowness (rows * cols calls).
# #     - Whole-table-at-once is fast but unreliable: Tesseract's page
# #       segmentation assumes flowing text, so it merges adjacent cells'
# #       text into single "words" and misreads grid lines as characters.
# #     - Per-row is the sweet spot: a row genuinely *is* one line of text,
# #       so Tesseract segments it correctly, and it cuts subprocess calls
# #       down to just the row count.

# #     Before trusting any OCR result, each cell is first checked for ink
# #     density on the (pre-cleanup) binary `thresh` image. A cell that's
# #     essentially blank -- a lone "-" -- can get misread by Tesseract as a
# #     stray digit or symbol; treating any near-empty cell as blank instead
# #     of trusting that guess avoids phantom marks like a "-" becoming "2".
# #     """
# #     extracted_grid = []
# #     pad = 4
# #     for row in grid_rows:
# #         rx0 = max(0, min(b[0] for b in row) - pad)
# #         ry0 = max(0, min(b[1] for b in row) - pad)
# #         rx1 = min(cleaned_gray.shape[1], max(b[0] + b[2] for b in row) + pad)
# #         ry1 = min(cleaned_gray.shape[0], max(b[1] + b[3] for b in row) + pad)
# #         row_crop = cleaned_gray[ry0:ry1, rx0:rx1]

# #         sparse = []
# #         for (x, y, w, h) in row:
# #             inner = thresh[y + 4:y + h - 4, x + 4:x + w - 4]
# #             ink = int(np.count_nonzero(inner)) if inner.size else 0
# #             sparse.append(ink < INK_THRESHOLD)

# #         data = pytesseract.image_to_data(
# #             row_crop, config="--oem 1 --psm 7", output_type=Output.DICT
# #         )

# #         col_words = {c_idx: [] for c_idx in range(len(row))}
# #         n = len(data["text"])
# #         for i in range(n):
# #             word = data["text"][i].strip()
# #             if not word:
# #                 continue
# #             wx = data["left"][i] + data["width"][i] / 2 + rx0
# #             for c_idx, (x, y, w, h) in enumerate(row):
# #                 if x <= wx <= x + w:
# #                     col_words[c_idx].append((data["left"][i], word))
# #                     break

# #         row_texts = []
# #         for c_idx in range(len(row)):
# #             if sparse[c_idx]:
# #                 row_texts.append("")
# #                 continue
# #             words = sorted(col_words[c_idx], key=lambda t: t[0])
# #             row_texts.append(" ".join(w for _, w in words).strip())
# #         extracted_grid.append(row_texts)

# #     return extracted_grid


# # @app.route("/")
# # def home():
# #     return render_template("index.html")

# # @app.route("/guide")
# # def guide_page():
# #     return render_template("bs.html")

# # @app.route("/process-image", methods=["POST"])
# # def process_image():
# #     if "file" not in request.files:
# #         return jsonify({"error": "No file uploaded"}), 400

# #     file = request.files["file"]
# #     if file.filename == "":
# #         return jsonify({"error": "No selected file"}), 400

# #     # Wait up to 90s for another upload's OCR to finish rather than
# #     # racing it for the same fractional CPU. This is what turns
# #     # concurrent users into a short queue instead of a hang.
# #     acquired = _ocr_lock.acquire(timeout=90)
# #     if not acquired:
# #         return jsonify({
# #             "error": "Server is busy processing another upload right now. Please try again in a few seconds."
# #         }), 503

# #     try:
# #         image_bytes = file.read()
# #         pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

# #         max_width = 1200
# #         if pil_img.width > max_width:
# #             ratio = max_width / float(pil_img.width)
# #             new_height = int(float(pil_img.height) * ratio)
# #             pil_img = pil_img.resize((max_width, new_height), Image.Resampling.LANCZOS)

# #         img = np.array(pil_img)
# #         gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

# #         thresh = cv2.threshold(
# #             gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
# #         )[1]

# #         h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
# #         v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))

# #         h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
# #         v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

# #         table_grid = cv2.add(h_lines, v_lines)

# #         contours, _ = cv2.findContours(
# #             table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
# #         )

# #         boxes = []
# #         for c in contours:
# #             x, y, w, h = cv2.boundingRect(c)
# #             if w > 20 and h > 12 and w < img.shape[1] * 0.9:
# #                 boxes.append((x, y, w, h))

# #         if not boxes:
# #             return jsonify({"error": "Could not detect table grid lines"}), 400

# #         boxes = sorted(boxes, key=lambda b: b[1])

# #         row_threshold = 12
# #         grid_rows = []
# #         for box in boxes:
# #             placed = False
# #             for r in grid_rows:
# #                 avg_y = sum(b[1] for b in r) / len(r)
# #                 if abs(box[1] - avg_y) < row_threshold:
# #                     r.append(box)
# #                     placed = True
# #                     break
# #             if not placed:
# #                 grid_rows.append([box])

# #         for r in grid_rows:
# #             r.sort(key=lambda b: b[0])

# #         # --- Erase grid lines, then OCR once per ROW instead of once
# #         # per CELL (rows * cols subprocess calls -> just rows) ---
# #         cleaned_gray = erase_grid_lines(gray, table_grid)
# #         extracted_grid = ocr_grid_batch(cleaned_gray, thresh, grid_rows)

# #         header_row = extracted_grid[0]

# #         subjects = []
# #         subject_col_indices = []
# #         for idx, text in enumerate(header_row):
# #             cleaned = text.strip()
# #             if idx > 0 and cleaned.lower() not in ["subject", "total", ""] and len(cleaned) > 0:
# #                 subjects.append(cleaned)
# #                 subject_col_indices.append(idx)

# #         if not subjects and len(extracted_grid) > 0:
# #             num_cols = len(header_row)
# #             for idx in range(1, num_cols):
# #                 subjects.append(header_row[idx] if header_row[idx] else f"Subject_{idx}")
# #                 subject_col_indices.append(idx)

# #         target_columns = [
# #             "Unit-1", "Unit-2", "Unit-3(1)", "Obj-1(A)", "Assignment-1(A)", "Internal-I total",
# #             "Unit-3(2)", "Unit-4", "Unit-5", "Obj-2(A)", "Assignment-2(A)", "Internal-II total"
# #         ]

# #         # Prioritize specific sub-keys (like unit-3(2)) before generic substrings (like unit-3)
# #         metric_map = {
# #             "unit-3(2)": "Unit-3(2)",
# #             "unit-3.2": "Unit-3(2)",
# #             "unit-3 (2)": "Unit-3(2)",
# #             "unit-3(1)": "Unit-3(1)",
# #             "unit-3.1": "Unit-3(1)",
# #             "unit-3": "Unit-3(1)",
# #             "unit-1": "Unit-1",
# #             "unit-2": "Unit-2",
# #             "obj-1(a)": "Obj-1(A)",
# #             "obj-i(a)": "Obj-1(A)",
# #             "assignment-1(a)": "Assignment-1(A)",
# #             "assignment-i(a)": "Assignment-1(A)",
# #             "internal-i total": "Internal-I total",
# #             "unit-4": "Unit-4",
# #             "unit-5": "Unit-5",
# #             "obj-2(a)": "Obj-2(A)",
# #             "assignment-2(a)": "Assignment-2(A)",
# #             "internal-ii total": "Internal-II total",
# #         }

# #         subject_data = {s: {col: None for col in target_columns} for s in subjects}

# #         for r_idx in range(1, len(extracted_grid)):
# #             row = extracted_grid[r_idx]
# #             if not row:
# #                 continue

# #             raw_label = row[0].lower().strip()
# #             matched_key = None

# #             for k, v in metric_map.items():
# #                 if k in raw_label:
# #                     matched_key = v
# #                     break

# #             # Fallback based on structural row position if OCR label is unreadable
# #             if not matched_key and 0 < r_idx <= len(target_columns):
# #                 matched_key = target_columns[r_idx - 1]

# #             if not matched_key:
# #                 continue

# #             for s_idx, subject in enumerate(subjects):
# #                 col_idx = subject_col_indices[s_idx] if s_idx < len(subject_col_indices) else (s_idx + 1)
# #                 if col_idx < len(row):
# #                     cell_val = row[col_idx].replace(" ", "")
# #                     if cell_val and cell_val not in ["-", "--", "None", "null", "."]:
# #                         subject_data[subject][matched_key] = cell_val

# #         final_rows = []
# #         for s in subjects:
# #             s_dict = {"Subject": s}
# #             s_dict.update(subject_data[s])

# #             analytics = calculate_analytics(
# #                 u1=s_dict["Unit-1"],
# #                 u2=s_dict["Unit-2"],
# #                 u3=s_dict["Unit-3(1)"],
# #                 obj=s_dict["Obj-1(A)"],
# #                 assign=s_dict["Assignment-1(A)"],
# #                 mid2_u1=s_dict["Unit-3(2)"],
# #                 mid2_u2=s_dict["Unit-4"],
# #                 mid2_u3=s_dict["Unit-5"],
# #                 mid2_obj=s_dict["Obj-2(A)"],
# #                 mid2_assign=s_dict["Assignment-2(A)"],
# #             )

# #             s_dict.update(analytics)
# #             final_rows.append(s_dict)

# #         gc.collect()
# #         return jsonify({"rows": final_rows})

# #     except Exception as e:
# #         gc.collect()
# #         return jsonify({"error": str(e)}), 500
# #     finally:
# #         _ocr_lock.release()

# # if __name__ == "__main__":
# #     port = int(os.environ.get("PORT", 5000))
# #     # threaded=True only helps a little for local testing; for real
# #     # multi-user traffic, run this behind gunicorn instead (see below).
# #     app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
import os
# Must be set before any Tesseract subprocess is spawned. On a throttled
# / fractional-CPU host (e.g. Render free tier), Tesseract's default
# internal multi-threading just adds scheduling overhead with no real
# extra core to use -- forcing 1 thread is measurably faster there.
os.environ.setdefault("OMP_THREAD_LIMIT", "1")
import gc
import io
import math
import threading
import cv2
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
app = Flask(__name__)
CORS(app)
# Free-tier hosts give you a fraction of one CPU core, not real
# parallelism. Rather than let concurrent uploads fight over that sliver
# of CPU (which is what was causing the "stuck on loading" behavior),
# serialize OCR work: one job runs at a time, others wait their turn.
_ocr_lock = threading.Lock()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
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
def erase_grid_lines(gray, table_grid):
    """
    Paint over the detected table grid lines so Tesseract doesn't read
    them as stray characters (vertical borders get misread as '|', '*',
    etc. and corrupt neighboring words) -- this is what made a single
    whole-table OCR pass unreliable.
    """
    line_mask = cv2.dilate(table_grid, np.ones((3, 3), np.uint8), iterations=1)
    cleaned = gray.copy()
    cleaned[line_mask > 0] = 255
    return cleaned
INK_DENSITY_THRESHOLD = 0.015  # 1.5% of cell area -- dashes measure <0.5%,
                                 # real marks measure 4.5%+, so this holds
                                 # up across different image resolutions
                                 # (unlike a hardcoded pixel count would)
def ocr_grid_batch(cleaned_gray, thresh, grid_rows):
    """
    Run Tesseract once PER ROW (not once per cell, and not once for the
    whole table).
    - Per-cell is accurate but spawns a subprocess per cell -- the main
      source of slowness (rows * cols calls).
    - Whole-table-at-once is fast but unreliable: Tesseract's page
      segmentation assumes flowing text, so it merges adjacent cells'
      text into single "words" and misreads grid lines as characters.
    - Per-row is the sweet spot: a row genuinely *is* one line of text,
      so Tesseract segments it correctly, and it cuts subprocess calls
      down to just the row count.
    Before trusting any OCR result, each cell is first checked for ink
    density on the (pre-cleanup) binary `thresh` image. A cell that's
    essentially blank -- a lone "-" -- can get misread by Tesseract as a
    stray digit or symbol; treating any near-empty cell as blank instead
    of trusting that guess avoids phantom marks like a "-" becoming "2".
    """
    extracted_grid = []
    pad = 4
    for row in grid_rows:
        rx0 = max(0, min(b[0] for b in row) - pad)
        ry0 = max(0, min(b[1] for b in row) - pad)
        rx1 = min(cleaned_gray.shape[1], max(b[0] + b[2] for b in row) + pad)
        ry1 = min(cleaned_gray.shape[0], max(b[1] + b[3] for b in row) + pad)
        row_crop = cleaned_gray[ry0:ry1, rx0:rx1]
        sparse = []
        for (x, y, w, h) in row:
            inner = thresh[y + 4:y + h - 4, x + 4:x + w - 4]
            if inner.size == 0:
                sparse.append(True)
                continue
            density = np.count_nonzero(inner) / inner.size
            sparse.append(density < INK_DENSITY_THRESHOLD)
        data = pytesseract.image_to_data(
            row_crop, config="--oem 1 --psm 7", output_type=Output.DICT
        )
        col_words = {c_idx: [] for c_idx in range(len(row))}
        n = len(data["text"])
        for i in range(n):
            word = data["text"][i].strip()
            if not word:
                continue
            wx = data["left"][i] + data["width"][i] / 2 + rx0
            for c_idx, (x, y, w, h) in enumerate(row):
                if x <= wx <= x + w:
                    col_words[c_idx].append((data["left"][i], word))
                    break
        row_texts = []
        for c_idx in range(len(row)):
            if sparse[c_idx]:
                row_texts.append("")
                continue
            words = sorted(col_words[c_idx], key=lambda t: t[0])
            row_texts.append(" ".join(w for _, w in words).strip())
        extracted_grid.append(row_texts)
    return extracted_grid
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/guide")
def guide_page():
    return render_template("bs.html")
@app.route("/process-image", methods=["POST"])
def process_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    # Wait up to 90s for another upload's OCR to finish rather than
    # racing it for the same fractional CPU. This is what turns
    # concurrent users into a short queue instead of a hang.
    acquired = _ocr_lock.acquire(timeout=90)
    if not acquired:
        return jsonify({
            "error": "Server is busy processing another upload right now. Please try again in a few seconds."
        }), 503
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
        # --- Erase grid lines, then OCR once per ROW instead of once
        # per CELL (rows * cols subprocess calls -> just rows) ---
        cleaned_gray = erase_grid_lines(gray, table_grid)
        extracted_grid = ocr_grid_batch(cleaned_gray, thresh, grid_rows)
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
        # Prioritize specific sub-keys (like unit-3(2)) before generic substrings (like unit-3)
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
            # Fallback based on structural row position if OCR label is unreadable
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
    finally:
        _ocr_lock.release()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # threaded=True only helps a little for local testing; for real
    # multi-user traffic, run this behind gunicorn instead (see below).
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
