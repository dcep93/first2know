const IS_LOCAL = false;
const FETCH_INTERVAL_MS = 10 * 1000;

export const url = IS_LOCAL
  ? "http://localhost:8000"
  : "https://dcep93-first2know-app.modal.run";

export function sfetch(url: string, options?: any) {
  return fetch(url, options)
    .then((resp) =>
      Promise.all([Promise.resolve(resp.ok), Promise.resolve(resp)])
    )
    .then(([ok, resp]) => {
      if (!ok)
        return resp.text().then((text) => {
          throw Error(text);
        });
      return resp;
    });
}

function iter() {
  sfetch(url).then(() => setTimeout(iter, FETCH_INTERVAL_MS));
}

sfetch(url)
  .then((resp) => resp.text())
  .then((text) => console.log(text))
  .then(iter);
