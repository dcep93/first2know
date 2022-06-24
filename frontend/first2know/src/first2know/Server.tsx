const IS_LOCAL = true;

export const modalUrl = IS_LOCAL
  ? "http://localhost:8000"
  : "https://dcep93-first2know-app.modal.run";
fetch(modalUrl)
  .then((resp) => resp.text())
  .then((text) => console.log(text));
