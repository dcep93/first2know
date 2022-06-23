import { useState } from "react";
import firebase, { AllToHandleType, ToHandleType } from "./firebase";
import styles from "./index.module.css";

function ShowCurrent(props: { allToHandle: AllToHandleType }): JSX.Element {
  return (
    <div>
      {Object.entries(props.allToHandle).map(([k, toHandle]) => (
        <RenderToHandle key={k} k={k} toHandle={toHandle} />
      ))}
    </div>
  );
}

// TODO dcep93 edit
function RenderToHandle(props: { k: string; toHandle: ToHandleType }) {
  const [hidden, update] = useState(true);
  return (
    <div>
      <pre className={styles.toHandlePre}>
        {JSON.stringify(props.toHandle, null, 2)}
      </pre>
      <div>
        <button onClick={() => update(!hidden)}>Toggle Image</button>
      </div>
      <img
        hidden={hidden}
        src={
          props.toHandle.data === undefined
            ? ""
            : `data:image/png;base64,${props.toHandle.data}`
        }
        alt=""
      ></img>
      <div>
        <button
          onClick={() => {
            if (window.confirm(`Do you really want to delete ${props.k}?`))
              firebase.deleteToHandle(props.k);
          }}
        >
          Delete {props.k}
        </button>
      </div>
    </div>
  );
}

export default ShowCurrent;
