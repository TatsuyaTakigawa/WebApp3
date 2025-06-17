# WebApp3

画像スタイル変換モデルを活用したWebアプリケーションです。ユーザーがアップロードした画像を、用意されたスタイル画像やユーザー指定のスタイル画像に変換することができます。

## 🖼️ 概要

本アプリは以下のような機能を提供します：

- ユーザーが画像をアップロード
- 任意のスタイル画像を選択またはアップロード
- スタイル変換を実行し、変換結果を表示・保存

TensorFlow Hub にて公開されている「Arbitrary Image Stylization」モデルを利用しています。

---

## 🚀 使用技術

- **Python 3.12.6**
- **Flask 3.1.1**：Webフレームワーク
- **TensorFlow 2.19.0**：画像スタイル変換モデル
- **Pillow**：画像処理ライブラリ

---

## 📦 インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/TatsuyaTakigawa/WebApp3.git
cd WebApp3
```

2. 仮想環境の作成（任意）

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

---

## 🖥️ 実行方法

```bash
python app.py
```

ブラウザで [http://localhost:5000](http://localhost:5000) にアクセス。

---

## 🧠 使用モデルについて

TensorFlow Hub で提供されている [Arbitrary Image Stylization v1](https://www.kaggle.com/models/google/arbitrary-image-stylization-v1/code) モデルを使用しています。

このモデルは以下を入力として受け取ります：

- content image（変換元画像）
- style image（変換先のスタイル）

そして、スタイルが適用された新しい画像を出力します。

---
