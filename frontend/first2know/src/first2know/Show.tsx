import { Link } from "react-router-dom";
import { AllToHandleType, ToHandleType } from "./firebase";
import styles from "./index.module.css";

function Show(props: {
  user: string;
  allToHandle: AllToHandleType;
}): JSX.Element {
  return (
    <div>
      {Object.entries(props.allToHandle).map(([k, toHandle]) => (
        <div key={k}>
          <RenderToHandle k={k} toHandle={toHandle} />
          <div>
            <Link to={`/${k}`}>Edit {k}</Link>
          </div>
        </div>
      ))}
    </div>
  );
}

export function RenderToHandle(props: { k: string; toHandle: ToHandleType }) {
  return (
    <div>
      <pre className={styles.toHandlePre}>
        {JSON.stringify(props.toHandle, null, 2)}
      </pre>
    </div>
  );
}

export default Show;
