import { Link } from "react-router-dom";
import { ToHandleType } from "./firebase";
import styles from "./index.module.css";

function Show(props: { toHandles: ToHandleType[] }): JSX.Element {
  return (
    <div className="monitorGrid">
      {props.toHandles.map((toHandle) => {
        const hasError = Boolean(toHandle.data_output.error);
        const status = toHandle.disabled
          ? "Disabled"
          : hasError
          ? "Error"
          : "Active";
        const statusClass = toHandle.disabled
          ? "statusPillDisabled"
          : hasError
          ? "statusPillOffline"
          : "statusPillOnline";
        const mode = toHandle.data_input.send_evaluation
          ? "Evaluation"
          : toHandle.data_input.selector
          ? "Element screenshot"
          : "Page screenshot";

        return (
          <article className="monitorCard" key={toHandle.key}>
            <header className="monitorCardHeader">
              <div className="monitorIdentity">
                <span className="monitorUrl">
                  {toHandle.data_input.url || "No URL configured"}
                </span>
                <code className="monitorKey">{toHandle.key}</code>
              </div>
              <div className="monitorMeta">
                <span className={`statusPill ${statusClass}`}>{status}</span>
                <Link className="buttonLink" to={`/${toHandle.key}`}>
                  Edit
                </Link>
              </div>
            </header>
            <div className="monitorSummary">
              <div>
                <span>Mode</span>
                <strong>{mode}</strong>
              </div>
              <div>
                <span>Stored time</span>
                <strong>
                  {new Date(
                    toHandle.data_output.time * 1000
                  ).toLocaleString()}
                </strong>
              </div>
            </div>
            <details className="monitorJson">
              <summary>View full JSON</summary>
              <RenderToHandle toHandle={toHandle} />
            </details>
          </article>
        );
      })}
    </div>
  );
}

export function RenderToHandle(props: { toHandle: ToHandleType }) {
  return (
    <div>
      <pre className={styles.toHandlePre}>
        {JSON.stringify(
          {
            age_s: Date.now() / 1000 - props.toHandle.data_output.time,
            ...props.toHandle,
          },
          null,
          2
        )}
      </pre>
    </div>
  );
}

export default Show;
