from flask import Flask, jsonify, render_template, request
from flask_compress import Compress
import json, threading, time, os
from datetime import datetime
from flask_caching import Cache


app = Flask(__name__, static_url_path='/static', template_folder='template')
Compress(app)

app.config['APPLICATION_ROOT'] = ''
app.config['COMPRESS_ALGORITHM'] = 'gzip'
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

cache = Cache(app)

JSON_FILE = f'{os.path.dirname(os.path.realpath(__file__))}/data.json'

if not os.path.isfile(JSON_FILE):
    with open(JSON_FILE, "w", encoding='utf-8') as f:
        json.dump({"day": 0, "food": 0, "care": 0, "last": { "" : "" }}, f, ensure_ascii=False, indent=4)

Temp_food: int = 0
Temp_care: int = 0


def setData(data: str, value: int) -> None:
    dump = None
    with open(JSON_FILE, "r") as f:
        dump = json.load(f)
        dump[data] = value
    with open(JSON_FILE, "w", encoding='utf-8') as f:
        json.dump(dump, f, ensure_ascii=False, indent=4)

def updateTime():
    current_date = datetime.now().date()
    while True:
        now = datetime.now().date()
        if now != current_date:
            current_date = now
            setData("day", now.day())
        time.sleep(1000)

@app.route('/food', methods=['POST'])
def icr_food():
    global Temp_food
    Temp_food += 10
    Temp_food = min(Temp_food, 100)
    setData("food", Temp_food)
    print(Temp_food)
    return jsonify({'Temp_food': Temp_food})

@app.route('/care', methods=['POST'])
def icr_care():
    global Temp_care
    data = request.json.get('Temp_care')
    Temp_care = data
    Temp_care = min(Temp_care, 100)
    setData("care", Temp_care)
    return jsonify({'Temp_care': f"{Temp_care}"})

@app.route('/get_value', methods=['GET'])
def get_value():
    global Temp_food, Temp_care
    with open(JSON_FILE, 'r') as f:
        dump = json.load(f)
        Temp_food = dump['food']
        Temp_care = dump['care']
        return jsonify({'current_value': dump})

def updateNeeds() -> None:
    dump = None
    while True:
        with open(JSON_FILE, "r") as f:
            dump = json.load(f)
            dump['food'] = max(dump['food'] - 1, 0)
            dump['care'] = max(dump['care'] - 1, 0)
        with open(JSON_FILE, "w", encoding='utf-8') as f:
            json.dump(dump, f, ensure_ascii=False, indent=4)
        print("au scazut valorile")
        time.sleep(360)

@app.route('/')
def index():
    return render_template('index.html')

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

if __name__ == '__main__':
    threading.Thread(target=updateTime, daemon=True).start()
    threading.Thread(target=updateNeeds, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')
