from flask import Flask, request, jsonify
from split_letters import split_letters
import os
from pathlib import Path

app = Flask(__name__)

UPLOAD_FOLDER = 'backend/uploads'
OUTPUT_FOLDER = 'backend/split_letters_output'

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'status': 'error', 'error': 'Invalid file format'}), 400

    # Save uploaded image
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    # Process image
    result = split_letters(image_path, OUTPUT_FOLDER)
    
    if result['status'] == 'error':
        return jsonify(result), 400
    elif result['status'] == 'warning':
        return jsonify(result), 200
    else:
        return jsonify({
            'status': 'success',
            'message': f"Processed {result['letter_count']} letters",
            'output_folder': result['output_folder']
        }), 200

if __name__ == '__main__':
    app.run(debug=True)