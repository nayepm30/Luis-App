from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image
import os
import io
import requests

app = Flask(__name__)
UPLOAD_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Usar variable de entorno para proteger tu clave API
REMOVE_BG_API_KEY = os.environ.get('REMOVE_BG_API_KEY')

@app.route('/')
def index():
    filename = request.args.get('filename')
    return render_template('index.html', filename=filename)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return 'No se encontró la imagen', 400

    image_file = request.files['image']
    if image_file.filename == '':
        return 'Nombre de archivo vacío', 400

    # Enviar imagen a la API de remove.bg
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': image_file},
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVE_BG_API_KEY}
    )

    if response.status_code != 200:
        return f"Error al quitar fondo: {response.status_code} - {response.text}", 500

    # Procesar imagen sin fondo
    image_no_bg = Image.open(io.BytesIO(response.content)).convert("RGBA")
    image_no_bg.thumbnail((500, 500), Image.LANCZOS)

    background = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
    x = (500 - image_no_bg.width) // 2
    y = (500 - image_no_bg.height) // 2
    background.paste(image_no_bg, (x, y), image_no_bg)

    final_image = background.convert("RGB")
    output_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    final_image.save(output_path)

    return redirect(url_for('index', filename=image_file.filename))

@app.route('/processed/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
