import cv2
import os
import numpy as np
from pathlib import Path

def split_letters(image_path, output_folder):
    """
    Split an A4 image containing Hebrew letters into individual letter images.
    
    Args:
        image_path (str): Path to the input image (e.g., PNG/JPG in uploads/)
        output_folder (str): Path to save the split letter images (e.g., split_letters_output/)
    
    Returns:
        dict: {'status': str, 'output_folder': str, 'letter_count': int, 'error': str (optional)}
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Validate input image
    if not os.path.exists(image_path) or not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return {
            'status': 'error',
            'error': 'Invalid or missing image file. Only PNG, JPG, or JPEG are supported.'
        }

    # Read and preprocess image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {
            'status': 'error',
            'error': 'Failed to load image.'
        }

    # Threshold and morphological operations
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    clean = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Find contours and bounding boxes
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in contours]

    def iou(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        return interArea / float(boxAArea + boxBArea - interArea + 1e-5)

    def merge_overlapping_boxes(boxes, iou_threshold=0.2, proximity=20):
        merged = []
        used = [False] * len(boxes)
        for i in range(len(boxes)):
            if used[i]:
                continue
            x1, y1, w1, h1 = boxes[i]
            new_box = [x1, y1, w1, h1]
            used[i] = True
            for j in range(i + 1, len(boxes)):
                if used[j]:
                    continue
                x2, y2, w2, h2 = boxes[j]
                if iou(new_box, [x2, y2, w2, h2]) > iou_threshold or (
                    abs(x1 - x2) < proximity and abs(y1 - y2) < proximity
                ):
                    nx = min(new_box[0], x2)
                    ny = min(new_box[1], y2)
                    nw = max(new_box[0] + new_box[2], x2 + w2) - nx
                    nh = max(new_box[1] + new_box[3], y2 + h2) - ny
                    new_box = [nx, ny, nw, nh]
                    used[j] = True
            merged.append(new_box)
        return merged

    # Merge overlapping boxes
    merged = merge_overlapping_boxes(boxes)

    # Filter small or nested boxes
    filtered = []
    for x, y, w, h in merged:
        if w * h < 60:  # Minimum area threshold
            continue
        inside = False
        for ox, oy, ow, oh in merged:
            if (x, y, w, h) != (ox, oy, ow, oh) and x >= ox and y >= oy and x + w <= ox + ow and y + h <= oy + oh:
                inside = True
                break
        if not inside:
            filtered.append([x, y, w, h])

    # Organize boxes into rows
    filtered.sort(key=lambda b: b[1])
    rows = []
    for b in filtered:
        x, y, w, h = b
        placed = False
        for row in rows:
            if abs(row[0][1] - y) < h:
                row.append(b)
                placed = True
                break
        if not placed:
            rows.append([b])

    # Sort rows and boxes (right to left for Hebrew)
    rows.sort(key=lambda r: r[0][1])
    ordered = []
    for row in rows:
        row.sort(key=lambda b: -b[0])
        ordered.extend(row)

    # Hebrew letters mapping
    hebrew_letters = [
        'alef', 'bet', 'gimel', 'dalet', 'he', 'vav', 'zayin', 'het', 'tet',
        'yod', 'kaf', 'lamed', 'mem', 'nun', 'samekh', 'ayin', 'pe', 'tsadi',
        'qof', 'resh', 'shin', 'tav', 'final_kaf', 'final_mem', 'final_nun', 'final_pe', 'final_tsadi'
    ]

    # Save cropped letters
    padding = 10
    letter_count = 0
    for i, (x, y, w, h) in enumerate(ordered[:27]):
        x1, y1 = max(x - padding, 0), max(y - padding, 0)
        x2, y2 = min(x + w + padding, img.shape[1]), min(y + h + padding, img.shape[0])
        crop = img[y1:y2, x1:x2]
        name = hebrew_letters[i]
        output_path = os.path.join(output_folder, f"{i:02d}_{name}.png")
        cv2.imwrite(output_path, crop)
        letter_count += 1

    # Validate output
    if letter_count < 27:
        return {
            'status': 'warning',
            'output_folder': output_folder,
            'letter_count': letter_count,
            'error': f'Expected 27 letters, but only {letter_count} were detected.'
        }

    return {
        'status': 'success',
        'output_folder': output_folder,
        'letter_count': letter_count
    }