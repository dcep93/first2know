import { useCallback, useEffect, useState } from "react";

const IS_LOCAL = window.location.search.includes("local");
const FETCH_INTERVAL_MS = 1000;

export const url = IS_LOCAL
  ? "http://localhost:8000"
  : "https://desktop-2uo8g83.tail789685.ts.net";

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
  const online = resp?.status_code === 200;
  return (
    <section className="serverPanel">
      <div className="panelHeading">
        <div>
          <h2>Backend status</h2>
          <p>The complete live health response refreshes every second.</p>
        </div>
        <span
          className={`statusPill ${
            online ? "statusPillOnline" : "statusPillOffline"
          }`}
        >
          {online ? "Online" : "Connecting"}
        </span>
      </div>
      <pre className="serverOutput">{JSON.stringify(resp, null, 2)}</pre>
    </section>
  );
}
