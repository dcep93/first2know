import { useState } from "react";
import { AllToHandleType, ToHandleType } from "./firebase";

// TODO dcep93 implement
function ShowCurrent(props: { allToHandle: AllToHandleType }): JSX.Element {
  return (
    <div>
      {Object.entries(props.allToHandle).map(([key, toHandle]) =>
        RenderToHandle(key, toHandle)
      )}
    </div>
  );
}

function RenderToHandle(key: string, toHandle: ToHandleType): JSX.Element {
  const [hidden, update] = useState(true);
  return (
    <div>
      <pre>{JSON.stringify(toHandle, null, 2)}</pre>
      <div>
        <button onClick={() => update(!hidden)}>Toggle Image</button>
      </div>
      <img
        hidden={hidden}
        src={`data:image/png;base64,${toHandle.data}`}
        alt=""
      ></img>
      <div>
        <button
          onClick={() => {
            if (window.confirm(`Do you really want to delete ${key}?`))
              alert("x");
          }}
        >
          Delete {key}
        </button>
      </div>
    </div>
  );
}

export default ShowCurrent;
