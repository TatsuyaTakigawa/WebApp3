document.addEventListener("DOMContentLoaded", () => {
  // プレビュー設定
  setupImagePreview("content_image_input", "content_preview", "label_content");
  setupImagePreview("style_image_input", "style_preview", "label_style");

  // フォーム送信時ローディング表示
  const form = document.querySelector("form");
  const loadingMessage = document.getElementById("loading_message");

  if (form && loadingMessage) {
    form.addEventListener("submit", () => {
      loadingMessage.style.display = "block";
    });
  }
});

/**
 * アップロード画像のプレビュー表示をセットアップする
 * @param {string} inputId - input要素のID
 * @param {string} previewId - プレビュー表示用の要素ID
 * @param {string} labelId - ラベル要素のID（ファイル名表示用）
 */
function setupImagePreview(inputId, previewId, labelId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  const label = document.getElementById(labelId);

  if (!input || !preview || !label) return;

  input.addEventListener("change", () => {
    preview.innerHTML = "";  // 前の画像をクリア

    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (e) => {
      const img = document.createElement("img");
      img.src = e.target.result;
      img.alt = "プレビュー画像";
      img.classList.add("preview-image");
      preview.appendChild(img);

      // ラベルの色など変えるならここで
      label.classList.add("selected");
    };

    reader.readAsDataURL(file);
  });
}
