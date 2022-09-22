import { Link, useNavigate } from "react-router-dom";
import firebase, { AllToHandleType, ToHandleType, UserType } from "./firebase";
import { RenderToHandle } from "./Show";
import ToHandle from "./ToHandle";

function Edit(props: {
  k: string;
  user: UserType;
  allToHandle: AllToHandleType;
}) {
  const toHandle = props.allToHandle[props.k];
  return (
    <>
      <RoutedEdit
        k={props.k}
        user={props.user}
        toHandle={toHandle}
        allToHandle={props.allToHandle}
      />
      <div>
        <Link to="/">Home</Link>
      </div>
    </>
  );
}

function RoutedEdit(props: {
  user: UserType;
  k: string;
  toHandle: ToHandleType;
  allToHandle: AllToHandleType;
}) {
  const navigate = useNavigate();
  if (!props.toHandle) return <pre>key not found: {props.k}</pre>;
  return (
    <>
      <ToHandle
        user={props.user}
        toHandle={props.toHandle}
        submit={(data_input) =>
          firebase
            .updateToHandle(props.k, {
              data_input,
              data_output: {
                ...props.toHandle.data_output,
                times: [Date.now() / 1000],
              },
              user: props.user,
            })
            .then(() => props.k)
        }
        allToHandle={props.allToHandle}
      />
      <button
        onClick={() => {
          if (window.confirm(`Do you really want to delete ${props.k}?`))
            firebase.deleteToHandle(props.k).then(() => navigate("/"));
        }}
      >
        Delete {props.k}
      </button>
      <div>
        <RenderToHandle k={props.k} toHandle={props.toHandle} />
      </div>
    </>
  );
}

// export function encrypt(
//   data_input: DataInputType,
//   user: UserType,
//   old_encrypted: string | null
// ): Promise<string> {
//   const body = JSON.stringify({
//     ...data_input,
//     user,
//     old_encrypted,
//   });
//   delete data_input.params!["cookie"];
//   return sfetch(`${url}/encrypt`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body,
//   }).then((resp) => resp.text());
// }

export default Edit;
