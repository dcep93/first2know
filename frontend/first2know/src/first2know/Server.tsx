const IS_LOCAL = false;

export const url = IS_LOCAL
  ? "http://localhost:8000"
  : "https://dcep93-first2know-app.modal.run";
fetch(url)
  .then((resp) => resp.text())
  .then((text) => console.log(text));
