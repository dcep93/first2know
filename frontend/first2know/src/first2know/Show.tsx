import { Link } from "react-router-dom";
import { ToHandleType } from "./firebase";
import styles from "./index.module.css";

function Show(props: { toHandles: ToHandleType[] }): JSX.Element {
  return (
    <div className="monitorGrid">
      {props.toHandles.map((toHandle) => (
        <article className="monitorCard" key={toHandle.key}>
          <header className="monitorCardHeader">
            <div className="monitorIdentity">
              <strong>{toHandle.key}</strong>
              <span>{toHandle.data_input.url || "No URL configured"}</span>
            </div>
            <div className="monitorMeta">
              <span
                className={`statusPill ${
                  toHandle.disabled ? "statusPillDisabled" : "statusPillOnline"
                }`}
              >
                {toHandle.disabled ? "Disabled" : "Active"}
              </span>
              <Link className="buttonLink" to={`/${toHandle.key}`}>
                Edit
              </Link>
            </div>
          </header>
          <div className="monitorJson">
            <RenderToHandle toHandle={toHandle} />
          </div>
        </article>
      ))}
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
