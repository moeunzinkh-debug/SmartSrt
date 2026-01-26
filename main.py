import os
import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

def get_seconds(time_str):
    h, m, s = time_str.strip().replace(',', '.').split(':')
    return float(h)*3600 + float(m)*60 + float(s)

def format_srt_time(total_seconds):
    if total_seconds < 0: total_seconds = 0
    td = datetime.timedelta(seconds=total_seconds)
    ms = int(td.microseconds / 1000)
    res = str(td).split('.')[0].zfill(8)
    return f"{res},{ms:03d}"

def process_srt(content):
    lines = content.splitlines()
    first_time = None
    for line in lines:
        if " --> " in line:
            first_time = get_seconds(line.split(" --> ")[0])
            break
    if first_time is None: return content
    new_lines = []
    for line in lines:
        if " --> " in line:
            start_str, end_str = line.split(" --> ")
            new_start = format_srt_time(get_seconds(start_str) - first_time)
            new_end = format_srt_time(get_seconds(end_str) - first_time)
            new_lines.append(f"{new_start} --> {new_end}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRT Resetter RGB Elite</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --bg: #f0f2f5; --card: #ffffff; --text: #333; --border: #eee;
        }
        [data-theme="dark"] {
            --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --border: #333;
        }
        body {
            font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text);
            margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh;
            transition: 0.3s; overflow-x: hidden;
        }
        /* RGB Border Animation */
        .rgb-box {
            position: relative; padding: 5px; background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
            background-size: 400%; border-radius: 20px; animation: rgb-move 20s linear infinite;
        }
        @keyframes rgb-move { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        
        .container { background: var(--card); padding: 40px; border-radius: 15px; width: 90%; max-width: 700px; text-align: center; }
        textarea {
            width: 100%; height: 200px; border-radius: 10px; border: 1px solid var(--border);
            padding: 15px; background: var(--card); color: var(--text); box-sizing: border-box; font-family: monospace;
        }
        .theme-btn { position: fixed; top: 20px; right: 20px; padding: 10px; cursor: pointer; border-radius: 50%; border: none; font-size: 20px; background: var(--card); color: var(--text); box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin: 10px; color: white; transition: 0.3s; }
        .btn-blue { background: #4A90E2; } .btn-green { background: #2ecc71; } .btn-red { background: #e74c3c; }
        .btn:hover { transform: scale(1.05); }
    </style>
</head>
<body onclick="shootFirework(event)">
    <button class="theme-btn" onclick="toggleTheme(event)">🌓</button>
    
    <div class="rgb-box">
        <div class="container">
            <h2>⏱️ SRT Time Resetter</h2>
            <form method="post">
                <textarea name="srt_text" id="inputSrt" placeholder="បិទភ្ជាប់ SRT នៅទីនេះ...">{{ original }}</textarea>
                <div>
                    <button type="submit" class="btn btn-blue">🚀 រៀបចំម៉ោង</button>
                    <button type="button" class="btn btn-red" onclick="clearAll(event)">🗑️ លុប</button>
                </div>
            </form>
            {% if result %}
            <hr style="border: 0.5px solid var(--border)">
            <textarea id="resultSrt">{{ result }}</textarea><br>
            <button class="btn btn-green" onclick="copyToClipboard(event)">📋 ចម្លង (Copy)</button>
            {% endif %}
        </div>
    </div>

    <script>
        function toggleTheme(e) {
            e.stopPropagation();
            const body = document.body;
            body.setAttribute('data-theme', body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
        }
        function shootFirework(e) {
            confetti({
                particleCount: 100, spread: 70, origin: { x: e.clientX / window.innerWidth, y: e.clientY / window.innerHeight },
                colors: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff']
            });
        }
        function copyToClipboard(e) {
            e.stopPropagation();
            var copyText = document.getElementById("resultSrt");
            copyText.select();
            document.execCommand("copy");
            alert("បានចម្លងរួចរាល់!");
        }
        function clearAll(e) {
            e.stopPropagation();
            document.getElementById("inputSrt").value = "";
            window.location.href = "/";
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
