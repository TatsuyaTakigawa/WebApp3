// static/script.js

function setupImagePreview(inputId, previewId, labelId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  const label = document.getElementById(labelId);

  input.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.innerHTML = `<img src="${e.target.result}" alt="プレビュー画像" style="max-width: 300px; margin-top: 10px;" />`;
      };
      reader.readAsDataURL(file);

      // ラベルのテキスト変更＆input再追加
      label.textContent = 'アップロード済み';
      label.appendChild(this);
    }
  });
}

// DOMがすべて読み込まれたら実行
document.addEventListener("DOMContentLoaded", function () {
  setupImagePreview('content_image_input', 'content_preview', 'label_content');
  setupImagePreview('style_image_input', 'style_preview', 'label_style');
});
