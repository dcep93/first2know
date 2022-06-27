const IS_LOCAL = false;
const FETCH_INTERVAL_MS = 10 * 1000;

export const url = IS_LOCAL
  ? "http://localhost:8000"
  : "https://dcep93-first2know-app.modal.run";
fetch(url)
  .then((resp) => resp.text())
  .then((text) => console.log(text))
  .then(() => setInterval(() => fetch(url), FETCH_INTERVAL_MS));
