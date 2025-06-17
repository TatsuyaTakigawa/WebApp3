import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect, session
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image

# === 環境変数の読み込み === #
load_dotenv()

# === Flaskアプリ設定 === #
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# === ディレクトリ設定 === #
BASE_DIR = 'static/images'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'upload')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
STYLE_FOLDER = os.path.join(BASE_DIR, 'styles')

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STYLE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config.update({
    'UPLOAD_FOLDER': UPLOAD_FOLDER,
    'OUTPUT_FOLDER': OUTPUT_FOLDER,
    'STYLE_FOLDER': STYLE_FOLDER
})

# === スタイル一覧（プリセット） === #
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

# === モデル読み込み === #
STYLE_MODEL_URL = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_model = hub.load(STYLE_MODEL_URL)

# === 許可ファイル拡張子 === #
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# === 画像読み込み関数 === #
def load_image(image_path, target_size=None):
    try:
        img = Image.open(image_path).convert('RGB')
        if target_size:
            img = img.resize(target_size)
        img = np.array(img).astype(np.float32)[np.newaxis, ...] / 255.0
        return img
    except Exception as e:
        raise ValueError(f"画像の読み込みに失敗しました: {e}")

# === 画像保存関数 === #
def save_image(np_image, save_path):
    img = np.clip(np_image[0], 0, 1)
    img = (img * 255).astype(np.uint8)
    Image.fromarray(img).save(save_path)

# === ファイル名生成関数 === #
def generate_secure_filename(filename):
    return secure_filename(f"{uuid.uuid4().hex}_{filename}")

# === 拡張子チェック === #
def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === スタイル画像取得関数 === #
def get_style_image(style_upload, style_filename):
    if style_upload and style_upload.filename:
        if not is_allowed_file(style_upload.filename):
            raise ValueError("スタイル画像はpng/jpg/jpegのみ対応しています。")
        filename = generate_secure_filename(style_upload.filename)
        path = os.path.join(app.config['STYLE_FOLDER'], filename)
        style_upload.save(path)
        url = url_for('static', filename=f"images/styles/{filename}")
        image = load_image(path, target_size=(256, 256))
        return image, url
    elif style_filename in STYLES:
        path = os.path.join(app.config['STYLE_FOLDER'], style_filename)
        image = load_image(path, target_size=(256, 256))
        url = url_for('static', filename=f"images/styles/{style_filename}")
        return image, url
    else:
        raise ValueError("スタイル画像を選択またはアップロードしてください。")

# === メイン画面：アップロードと変換処理 === #
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files.get('content_image')
        if not uploaded_file or uploaded_file.filename == '':
            return "変換したい画像をアップロードしてください。", 400
        if not is_allowed_file(uploaded_file.filename):
            return "対応していないファイル形式です。png/jpg/jpegのみ対応。", 400

        try:
            # コンテンツ画像の保存
            content_filename = generate_secure_filename(uploaded_file.filename)
            content_path = os.path.join(app.config['UPLOAD_FOLDER'], content_filename)
            uploaded_file.save(content_path)

            # スタイル画像の取得
            style_image, style_url = get_style_image(
                request.files.get('style_image_upload'),
                request.form.get('style_image')
            )

            # 画像の読み込みと変換
            content_image = load_image(content_path)
            outputs = hub_model(tf.constant(content_image), tf.constant(style_image))
            stylized_image = outputs[0]

            # 出力画像の保存
            output_filename = f"stylized_{content_filename}"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            save_image(stylized_image.numpy(), output_path)

            # セッションに画像情報を保存
            session['result'] = {
                'content_image': f"images/upload/{content_filename}",
                'style_image': style_url.replace('/static/', ''),
                'output_image': f"images/output/{output_filename}"
            }

            return redirect(url_for('result'))

        except Exception as e:
            return f"エラーが発生しました: {e}", 500

    return render_template('index.html', styles=STYLES)

# === 結果表示ページ === #
@app.route('/result')
def result():
    result = session.get('result')
    if not result:
        return redirect(url_for('index'))

    return render_template(
        'result.html',
        content_image=url_for('static', filename=result['content_image']),
        style_image=url_for('static', filename=result['style_image']),
        output_image=url_for('static', filename=result['output_image'])
    )

# === エントリーポイント === #
if __name__ == '__main__':
    app.run(debug=True)
