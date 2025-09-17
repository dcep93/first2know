import { Link, useNavigate } from "react-router-dom";
import firebase, { ToHandleType } from "./firebase";
import { RenderToHandle } from "./Show";
import ToHandle from "./ToHandle";

function Edit(props: { toHandle: ToHandleType }) {
  return (
    <>
      <RoutedEdit toHandle={props.toHandle} />
      <div>
        <Link to="/">Home</Link>
      </div>
    </>
  );
}

function RoutedEdit(props: { toHandle: ToHandleType }) {
  const navigate = useNavigate();
  return (
    <>
      <ToHandle
        toHandle={props.toHandle}
        submit={(data_input) =>
          firebase
            .updateToHandle({
              ...props.toHandle,
              data_input,
              data_output:
                props.toHandle.data_output === null
                  ? {
                      time: Date.now() / 1000,
                      screenshot_data: null,
                      error: null,
                    }
                  : {
                      ...props.toHandle.data_output,
                      time: Date.now() / 1000,
                      error: null,
                    },
            })
            .then(() => props.toHandle.key)
        }
      />
      <button
        onClick={() => {
          if (
            window.confirm(
              `Do you really want to delete ${props.toHandle.key}?`
            )
          )
            firebase
              .deleteToHandle(props.toHandle.key)
              .then(() => navigate("/"));
        }}
      >
        Delete {props.toHandle.key}
      </button>
      <div>
        <RenderToHandle toHandle={props.toHandle} />
      </div>
    </>
  );
}

export default Edit;
