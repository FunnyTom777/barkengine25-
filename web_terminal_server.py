import sys
import io
from flask import Flask, request, jsonify
from flask_cors import CORS

globals_dict = {}

app = Flask(__name__)
CORS(app)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    output = ''
    error = ''
    try:
        exec(code, globals_dict)
        output = sys.stdout.getvalue()
        error = sys.stderr.getvalue()
    except Exception as e:
        output = sys.stdout.getvalue()
        error = sys.stderr.getvalue() + str(e)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    return jsonify({'output': output, 'error': error})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
