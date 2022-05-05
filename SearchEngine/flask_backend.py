import json
from flask import Flask, request, jsonify
from prepare_array import query_data, load_data_from_file
from flask_cors import CORS
from time import perf_counter

indexes1, A1, file_names1 = load_data_from_file('./main_data')

print('Array shape: ', A1.shape)

app = Flask(__name__)
CORS(app)

@app.route("/search", methods=['GET'])
def hello_world():
    args = request.args

    t0 = perf_counter()
    queried_data = query_data(args['query'], indexes1, A1, file_names1, k=15)
    tc = perf_counter() - t0

    result = {
        'data': queried_data,
        'time': round(tc, 2)
    }
    return jsonify(result)
