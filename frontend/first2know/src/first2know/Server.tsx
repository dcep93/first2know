import { useCallback, useEffect, useState } from "react";

const IS_LOCAL = window.location.search.includes("local");
const FETCH_INTERVAL_MS = 1000;

export const url = IS_LOCAL
  ? "http://localhost:8000"
  : "https://first2know-125082277118.us-east1.run.app";

export function clog<T>(t: T): T {
  console.log(t);
  return t;
}

var initializedIter = false;
export default function Server() {
  const [resp, update] = useState<any>(null);
  const iter = useCallback(() => {
    fetch(url)
      .then((resp) => resp.json())
      .catch((err) => err)
      .then(update)
      .then(() => setTimeout(iter, FETCH_INTERVAL_MS));
  }, []);
  useEffect(() => {
    if (initializedIter) return;
    initializedIter = true;
    iter();
  }, [iter]);
  return <pre>{JSON.stringify(resp, null, 2)}</pre>;
}
