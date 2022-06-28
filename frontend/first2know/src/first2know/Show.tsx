import { useState } from "react";
import { Link } from "react-router-dom";
import { AllToHandleType, ToHandleType } from "./firebase";
import styles from "./index.module.css";
import { isAdmin, UserType } from "./User";

function Show(props: {
  user: UserType | null;
  allToHandle: AllToHandleType;
}): JSX.Element {
  return (
    <div>
      {Object.entries(props.allToHandle)
        .filter(
          ([k, toHandle]) =>
            toHandle.user_name !== undefined || isAdmin(props.user)
        )
        .map(([k, toHandle]) => (
          <RenderToHandle key={k} k={k} toHandle={toHandle} />
        ))}
    </div>
  );
}

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
          props.toHandle.data_output.img_data === undefined
            ? ""
            : `data:image/png;base64,${props.toHandle.data_output.img_data}`
        }
        alt=""
      ></img>
      <div>
        <Link to={`/${props.k}`}>Edit {props.k}</Link>
      </div>
    </div>
  );
}

export default Show;
