import os
import subprocess
import sys
import threading
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE_DIR = "user_bots"
os.makedirs(BASE_DIR, exist_ok=True)

running_processes = {}
bot_logs = {} 

def stream_logs(bot_name, process):
    bot_logs[bot_name] = ""
    for line in iter(process.stdout.readline, b''):
        bot_logs[bot_name] += line.decode('utf-8', errors='replace')
        if len(bot_logs[bot_name]) > 50000:
            bot_logs[bot_name] = bot_logs[bot_name][-50000:]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/run', methods=['POST'])
def run_bot():
    data = request.json
    if not data or 'code' not in data or 'bot_name' not in data:
        return jsonify({"error": "Missing data"}), 400

    bot_name = secure_filename(data['bot_name'])
    code = data['code']
    
    bot_dir = os.path.join(BASE_DIR, bot_name)
    os.makedirs(bot_dir, exist_ok=True)
    
    bot_file = os.path.join(bot_dir, "main.py")
    with open(bot_file, "w", encoding="utf-8") as f:
        f.write(code)

    if bot_name in running_processes:
        running_processes[bot_name].terminate()

    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=bot_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False
        )
        running_processes[bot_name] = process
        threading.Thread(target=stream_logs, args=(bot_name, process), daemon=True).start()
        
        return jsonify({"status": "success", "message": f"Bot '{bot_name}' started!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/<bot_name>', methods=['GET'])
def get_logs(bot_name):
    bot_name = secure_filename(bot_name)
    return jsonify({"logs": bot_logs.get(bot_name, "Starting...\n")})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    bot_name = secure_filename(request.json.get('bot_name', ''))
    if bot_name in running_processes:
        running_processes[bot_name].terminate()
        del running_processes[bot_name]
        return jsonify({"status": "success", "message": "Bot stopped."})
    return jsonify({"error": "Bot not running"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)