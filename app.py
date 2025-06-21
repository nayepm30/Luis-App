from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from PIL import Image
from rembg import remove
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Obtener nombre de archivo procesado si viene por parámetro query
    filename = request.args.get('filename')
    return render_template('index.html', filename=filename)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return 'No se encontró la imagen', 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return 'Nombre de archivo vacío', 400

    # Quitar fondo
    input_image = image_file.read()
    output_image_data = remove(input_image)

    # Convertir a imagen con PIL
    image_no_bg = Image.open(io.BytesIO(output_image_data)).convert("RGBA")
    image_no_bg.thumbnail((500, 500), Image.LANCZOS)

    # Crear fondo blanco
    background = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
    x = (500 - image_no_bg.width) // 2
    y = (500 - image_no_bg.height) // 2
    background.paste(image_no_bg, (x, y), image_no_bg)

    # Convertir a RGB y guardar
    final_image = background.convert("RGB")
    output_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
    final_image.save(output_path)

    # Redirigir a index con el nombre de la imagen para mostrarla
    return redirect(url_for('index', filename=image_file.filename))

@app.route('/processed/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
