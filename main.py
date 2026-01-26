import os
import re
import datetime
from flask import Flask, render_template_string, request

app = Flask(__name__)

# --- SRT Logic ---
def get_seconds(time_str):
    """ប្តូរពី HH:MM:SS,mmm ទៅជា វិនាទី"""
    h, m, s = time_str.strip().replace(',', '.').split(':')
    return float(h)*3600 + float(m)*60 + float(s)

def format_srt_time(total_seconds):
    """ប្តូរពី វិនាទី ត្រឡប់ទៅ HH:MM:SS,mmm វិញ"""
    if total_seconds < 0: total_seconds = 0
    td = datetime.timedelta(seconds=total_seconds)
    # បង្កើតទម្រង់ HH:MM:SS.mmm
    ms = int(td.microseconds / 1000)
    res = str(td).split('.')[0].zfill(8) # HH:MM:SS
    return f"{res},{ms:03d}"

def process_srt(content):
    lines = content.splitlines()
    first_time = None
    
    # រកមើលម៉ោងដំបូងបំផុតក្នុងឯកសារ
    for line in lines:
        if " --> " in line:
            first_time = get_seconds(line.split(" --> ")[0])
            break
            
    if first_time is None: return content

    new_lines = []
    for line in lines:
        if " --> " in line:
            start_str, end_str = line.split(" --> ")
            # ដកម៉ោងដំបូងចេញ ដើម្បីឱ្យវាចាប់ផ្តើមពី 00:00:00
            new_start = format_srt_time(get_seconds(start_str) - first_time)
            new_end = format_srt_time(get_seconds(end_str) - first_time)
            new_lines.append(f"{new_start} --> {new_end}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

# --- Web Interface ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SRT Time Resetter</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background: #f0f2f5; text-align: center; }
        textarea { width: 90%; height: 300px; border-radius: 10px; padding: 10px; border: 1px solid #ccc; font-family: monospace; }
        button { background: #007bff; color: white; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }
        button:hover { background: #0056b3; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h2>⏱️ SRT Time Resetter</h2>
        <p>បិទភ្ជាប់អត្ថបទ SRT របស់អ្នក ដើម្បីឱ្យវាចាប់ផ្ដើមពីនាទី <b>00:00:00</b> ឡើងវិញ</p>
        <form method="post">
            <textarea name="srt_text" placeholder="បិទភ្ជាប់ SRT នៅទីនេះ...">{{ original }}</textarea><br>
            <button type="submit">កែសម្រួលពេលវេលា</button>
        </form>
        {% if result %}
        <h3>✅ លទ្ធផល៖</h3>
        <textarea readonly>{{ result }}</textarea>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    original = ""
    if request.method == 'POST':
        original = request.form.get('srt_text', '')
        if original:
            result = process_srt(original)
    return render_template_string(HTML_TEMPLATE, original=original, result=result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
