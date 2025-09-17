import { Link } from "react-router-dom";
import { ToHandleType } from "./firebase";
import styles from "./index.module.css";

function Show(props: { toHandles: ToHandleType[] }): JSX.Element {
  return (
    <div>
      {props.toHandles.map((toHandle) => (
        <div key={toHandle.key}>
          <RenderToHandle toHandle={toHandle} />
          <div>
            <Link to={`/${toHandle.key}`}>Edit {toHandle.key}</Link>
          </div>
        </div>
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
