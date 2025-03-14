from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/FlowMapAPI.json', methods=['GET'])
def get_json():
    json_path = os.path.join(os.getcwd(), 'FlowMapAPI.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = f.read()
        return data, 200, {'Content-Type': 'application/json'}
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
