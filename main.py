import os
import datetime
import sys
import types
import re
from flask import Flask, render_template_string, request

# បង្កើត module cgi ក្លែងក្លាយដើម្បីការពារ Error លើ Python 3.13
mock_cgi = types.ModuleType('cgi')
mock_cgi.parse_header = lambda x: (x, {}) 
sys.modules['cgi'] = mock_cgi

app = Flask(__name__)

def get_seconds(time_str):
    try:
        h, m, s = time_str.strip().replace(',', '.').split(':')
        return float(h)*3600 + float(m)*60 + float(s)
    except: return 0

def format_srt_time(total_seconds):
    td = datetime.timedelta(seconds=max(0, total_seconds))
    ms = int(td.microseconds / 1000) if td.microseconds else 0
    res = str(td).split('.')[0].zfill(8)
    return f"{res},{ms:03d}"

def process_srt(content):
    lines = content.splitlines()
    first_time = None
    # រកមើលម៉ោងដំបូងបង្អស់
    for line in lines:
        if " --> " in line:
            try:
                first_time = get_seconds(line.split(" --> ")[0])
                break
            except: continue
    
    if first_time is None: return content

    new_lines = []
    current_index = 1
    
    for line in lines:
        clean_line = line.strip()
        
        # ១. ប្រសិនបើជាជួរម៉ោង
        if " --> " in clean_line:
            try:
                s, e = clean_line.split(" --> ")
                new_lines.append(f"{format_srt_time(get_seconds(s)-first_time)} --> {format_srt_time(get_seconds(e)-first_time)}")
            except: 
                new_lines.append(line)
        
        # ២. ប្រសិនបើជាជួរលេខរៀង (រៀបលេខរៀងចាប់ពី ១ ឡើងវិញ)
        elif clean_line.isdigit():
            new_lines.append(str(current_index))
            current_index += 1
            
        # ៣. ប្រសិនបើជាជួរអត្ថបទ (លុបអត្ថបទក្នុងដង្កៀប [] ចេញ)
        else:
            processed_text = re.sub(r'\[.*?\]', '', line).strip()
            # បើជាជួរទទេ ទុកជួរទទេ បើមានអត្ថបទ ដាក់អត្ថបទចូល
            if processed_text or not line.strip():
                new_lines.append(processed_text)
                
    return "\n".join(new_lines)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="km">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRT Resetter Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f1f5f9; --primary: #3b82f6; }
        body[data-theme="light"] { --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --primary: #2563eb; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; transition: 0.3s; }
        .outer-box { position: relative; width: 92%; max-width: 450px; padding: 3px; background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000); background-size: 400%; border-radius: 24px; animation: move 10s linear infinite; }
        @keyframes move { 0% {background-position: 0% 50%;} 100% {background-position: 100% 50%;} }
        .container { background: var(--card); border-radius: 22px; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        textarea { width: 100%; height: 160px; background: rgba(0,0,0,0.1); border: 1px solid rgba(128,128,128,0.2); border-radius: 15px; color: var(--text); padding: 15px; box-sizing: border-box; resize: none; outline: none; }
        .btn-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        button { padding: 14px; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        .btn-submit { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
        .btn-clear { background: #ef4444; }
        .btn-copy { background: #10b981; grid-column: span 2; margin-top: 5px; }
        .theme-toggle { position: absolute; top: -55px; right: 10px; background: var(--card); border: none; color: var(--text); padding: 10px; border-radius: 50%; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 100; }
    </style>
</head>
<body onclick="fire(event)">
    <div class="outer-box" onclick="event.stopPropagation()">
        <button type="button" class="theme-toggle" onclick="toggleT(event)">🌓</button>
        <div class="container">
            <h2 style="text-align:center;margin:0;">⏱️ SRT Resetter</h2>
            <form method="POST">
                <textarea name="srt_text" id="inputSrt" placeholder="បិទភ្ជាប់ SRT ទីនេះ...">{{ original }}</textarea>
                <div class="btn-row">
                    <button type="submit" class="btn-submit">🚀 Reset ម៉ោង</button>
                    <button type="button" class="btn-clear" onclick="clearA(event)">🗑️ លុប</button>
                </div>
            </form>
            {% if result %}
            <textarea id="resSrt" readonly>{{ result }}</textarea>
            <button type="button" class="btn-copy" onclick="copyC(event)">📋 ចម្លងអត្ថបទ</button>
            {% endif %}
        </div>
    </div>
    <script>
        function toggleT(e) { e.preventDefault(); e.stopPropagation(); const b = document.body; b.setAttribute('data-theme', b.getAttribute('data-theme') === 'light' ? 'dark' : 'light'); }
        function fire(e) { confetti({ particleCount: 40, spread: 60, origin: { x: e.clientX/window.innerWidth, y: e.clientY/window.innerHeight } }); }
        function copyC(e) { e.stopPropagation(); const t = document.getElementById("resSrt"); t.select(); document.execCommand("copy"); alert("ចម្លងរួចរាល់!"); }
        function clearA(e) { e.stopPropagation(); window.location.href = "/"; }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
