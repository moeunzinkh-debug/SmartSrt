import os
import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

def get_seconds(time_str):
    try:
        h, m, s = time_str.strip().replace(',', '.').split(':')
        return float(h)*3600 + float(m)*60 + float(s)
    except: return 0

def format_srt_time(total_seconds):
    td = datetime.timedelta(seconds=max(0, total_seconds))
    ms = int(td.microseconds / 1000)
    res = str(td).split('.')[0].zfill(8)
    return f"{res},{ms:03d}"

def process_srt(content):
    lines = content.splitlines()
    first_time = None
    for line in lines:
        if " --> " in line:
            try:
                first_time = get_seconds(line.split(" --> ")[0])
                break
            except: continue
    if first_time is None: return content
    new_lines = []
    for line in lines:
        if " --> " in line:
            try:
                s, e = line.split(" --> ")
                new_lines.append(f"{format_srt_time(get_seconds(s)-first_time)} --> {format_srt_time(get_seconds(e)-first_time)}")
            except: new_lines.append(line)
        else: new_lines.append(line)
    return "\n".join(new_lines)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SRT Resetter RGB Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        :root { --bg: #121212; --card: #1e1e1e; --text: #ffffff; --primary: #00d2ff; }
        [data-theme="light"] { --bg: #f0f2f5; --card: #ffffff; --text: #333333; --primary: #007bff; }
        
        body {
            background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif;
            margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh;
            transition: 0.3s;
        }
        
        /* RGB Border Container */
        .outer-box {
            position: relative; width: 90%; max-width: 500px; padding: 3px;
            background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
            background-size: 400%; border-radius: 20px; animation: move 10s linear infinite;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        @keyframes move { 0% {background-position: 0% 50%;} 100% {background-position: 100% 50%;} }

        .container {
            background: var(--card); border-radius: 18px; padding: 25px;
            display: flex; flex-direction: column; gap: 15px;
        }

        h2 { margin: 0; font-size: 22px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        
        textarea {
            width: 100%; height: 180px; background: rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px; color: var(--text); padding: 12px; box-sizing: border-box;
            font-family: monospace; font-size: 14px; resize: none; outline: none;
        }

        .btn-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        
        button {
            padding: 12px; border: none; border-radius: 10px; cursor: pointer;
            font-weight: bold; font-size: 14px; transition: 0.2s; color: white;
        }
        .btn-submit { background: linear-gradient(to right, #00d2ff, #3a7bd5); }
        .btn-clear { background: #ff4b2b; }
        .btn-copy { background: #2ecc71; grid-column: span 2; }
        
        button:active { transform: scale(0.95); }

        .theme-toggle {
            position: absolute; top: -50px; right: 0; background: var(--card);
            border: none; color: var(--text); padding: 10px; border-radius: 50%; cursor: pointer;
        }
    </style>
</head>
<body onclick="fire(event)">
    <div class="outer-box">
        <button class="theme-toggle" onclick="toggleT(event)">🌓</button>
        <div class="container">
            <h2>⏱️ SRT Time Resetter</h2>
            <form method="POST">
                <textarea name="srt_text" id="inputSrt" placeholder="បិទភ្ជាប់ SRT នៅទីនេះ...">{{ original }}</textarea>
                <div class="btn-row">
                    <button type="submit" class="btn-submit">🚀 រៀបចំម៉ោង</button>
                    <button type="button" class="btn-clear" onclick="clearA(event)">🗑️ លុប</button>
                </div>
            </form>
            {% if result %}
            <textarea id="resSrt" readonly>{{ result }}</textarea>
            <button class="btn-copy" onclick="copyC(event)">📋 ចម្លងអត្ថបទ</button>
            {% endif %}
        </div>
    </div>

    <script>
        function toggleT(e) {
            e.stopPropagation();
            const b = document.body;
            b.setAttribute('data-theme', b.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
        }
        function fire(e) {
            confetti({ particleCount: 60, spread: 50, origin: { x: e.clientX/window.innerWidth, y: e.clientY/window.innerHeight } });
        }
        function copyC(e) {
            e.stopPropagation();
            const t = document.getElementById("resSrt");
            t.select(); document.execCommand("copy");
            alert("Copy រួចរាល់!");
        }
        function clearA(e) {
            e.stopPropagation();
            document.getElementById("inputSrt").value = "";
            window.location.href = "/";
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    o, r = "", ""
    if request.method == 'POST':
        o = request.form.get('srt_text', '')
        if o: r = process_srt(o)
    return render_template_string(HTML_TEMPLATE, original=o, result=r)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
