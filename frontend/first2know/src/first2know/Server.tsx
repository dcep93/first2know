import { useEffect, useState } from "react";

const IS_LOCAL = window.location.search.includes("local");
const FETCH_INTERVAL_MS = 10 * 1000;

export const url = IS_LOCAL
  ? "http://localhost:8000"
  : "https://chromatic-realm-466116-n0.appspot.com";

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

export function clog<T>(t: T): T {
  console.log(t);
  return t;
}

export default function Server() {
  const [resp, update] = useState<string | null>(null);
  useEffect(() => {
    sfetch(url)
      .then((resp) => resp.text())
      .then(update)
      .then(iter);
  }, []);
  return <pre>{resp}</pre>;
}
