import { useState } from "react";
import { Link } from "react-router-dom";
import { AllToHandleType, ToHandleType, UserType } from "./firebase";
import styles from "./index.module.css";

function Show(props: {
  user: UserType;
  allToHandle: AllToHandleType;
}): JSX.Element {
  return (
    <div>
      {Object.entries(props.allToHandle).map(([k, toHandle]) => (
        <>
          <RenderToHandle key={k} k={k} toHandle={toHandle} />
          <div>
            <Link to={`/${k}`}>Edit {k}</Link>
          </div>
        </>
      ))}
    </div>
  );
}

export function RenderToHandle(props: { k: string; toHandle: ToHandleType }) {
  const [hidden, update] = useState(true);
  return (
    <div>
      <pre className={styles.toHandlePre}>
        {JSON.stringify(props.toHandle, null, 2)}
      </pre>
      <div>
        <button onClick={() => update(!hidden)}>Toggle Output</button>
      </div>
      <div hidden={hidden}>
        {props.toHandle.data_output?.screenshot_data && (
          <img
            src={props.toHandle.data_output.screenshot_data!.img_url}
            alt=""
          ></img>
        )}
        {props.toHandle.data_output?.error && (
          <pre>{JSON.stringify(props.toHandle.data_output.error, null, 2)}</pre>
        )}
      </div>
    </div>
  );
}

export default Show;
