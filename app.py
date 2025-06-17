import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image

app = Flask(__name__)

# パス設定
BASE_DIR = 'static/images'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'upload')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
STYLE_FOLDER = os.path.join(BASE_DIR, 'styles')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STYLE_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['STYLE_FOLDER'] = STYLE_FOLDER

# TensorFlow Hubのスタイル変換モデルをロード
hub_model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')

# 事前に登録されたスタイル画像一覧
STYLES = {
    "ukiyoe_person.jpg": "浮世絵（人物）",
    "ukiyoe_landscape.jpg": "浮世絵（風景）",
    "gogh_person.jpg": "ゴッホ（人物）",
    "gogh_landscape.jpg": "ゴッホ（風景）",
    "picasso_person.jpg": "ピカソ（人物）",
    "picasso_landscape.jpg": "ピカソ（風景）",
    "ghibli_person.jpg": "ジブリ（人物）",
    "ghibli_landscape.jpg": "ジブリ（風景）"
}

def load_image(image_path, target_size=None):
    img = Image.open(image_path).convert('RGB')
    if target_size:
        img = img.resize(target_size)
    img = np.array(img).astype(np.float32)[np.newaxis, ...] / 255.
    return img

def save_image(np_image, save_path):
    img = np_image[0]
    img = np.clip(img, 0, 1)
    img = (img * 255).astype(np.uint8)
    Image.fromarray(img).save(save_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # コンテンツ画像取得
        uploaded_file = request.files.get('content_image')
        if not uploaded_file or uploaded_file.filename == '':
            return "画像をアップロードしてください", 400

        # アップロード画像保存
        content_filename = secure_filename(uploaded_file.filename)
        content_path = os.path.join(app.config['UPLOAD_FOLDER'], content_filename)
        uploaded_file.save(content_path)

        # スタイル画像の選択 or アップロード
        style_filename = request.form.get('style_image')
        style_upload = request.files.get('style_image_upload')

        if style_upload and style_upload.filename != '':
            # アップロードされたスタイル画像を使用
            style_filename_up = secure_filename(style_upload.filename)
            style_path = os.path.join(app.config['STYLE_FOLDER'], style_filename_up)
            style_upload.save(style_path)
            style_image = load_image(style_path, target_size=(256, 256))
            style_image_url = url_for('static', filename=f"images/styles/{style_filename_up}")
        elif style_filename in STYLES:
            # プリセットのスタイル画像を使用
            style_path = os.path.join(app.config['STYLE_FOLDER'], style_filename)
            style_image = load_image(style_path, target_size=(256, 256))
            style_image_url = url_for('static', filename=f"images/styles/{style_filename}")
        else:
            return "スタイル画像が選択またはアップロードされていません", 400

        # コンテンツ画像読み込み
        content_image = load_image(content_path)

        # スタイル変換実行
        outputs = hub_model(tf.constant(content_image), tf.constant(style_image))
        stylized_image = outputs[0]

        # 出力ファイル保存
        output_filename = f"stylized_{content_filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        save_image(stylized_image.numpy(), output_path)

        return render_template('index.html', styles=STYLES,
                               content_image=url_for('static', filename=f"images/upload/{content_filename}"),
                               style_image=style_image_url,
                               output_image=url_for('static', filename=f"images/output/{output_filename}"))

    return render_template('index.html', styles=STYLES, content_image=None, style_image=None, output_image=None)

if __name__ == '__main__':
    app.run(debug=True)
