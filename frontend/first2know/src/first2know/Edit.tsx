import { Link, useNavigate } from "react-router-dom";
import firebase, { ToHandleType } from "./firebase";
import { RenderToHandle } from "./Show";
import ToHandle from "./ToHandle";

function Edit(props: { toHandle: ToHandleType }) {
  return (
    <div>
      <div className="backRow">
        <Link className="backLink" to="/">
          ← Home
        </Link>
      </div>
      <RoutedEdit toHandle={props.toHandle} />
    </div>
  );
}

function RoutedEdit(props: { toHandle: ToHandleType }) {
  const navigate = useNavigate();
  return (
    <div className="pageStack">
      <ToHandle
        toHandle={props.toHandle}
        submit={(data_input, disabled) =>
          firebase
            .updateToHandle({
              ...props.toHandle,
              disabled,
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
      <div className="dangerActions">
        <button
          className="dangerButton"
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
      </div>
      <section className="monitorCard rawDataPanel">
        <div className="panelHeading">
          <div>
            <h2>Raw monitor data</h2>
            <p>The complete decrypted state remains visible.</p>
          </div>
        </div>
        <RenderToHandle toHandle={props.toHandle} />
      </section>
    </div>
  );
}

export default Edit;
