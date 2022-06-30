import { Link, useNavigate } from "react-router-dom";
import firebase, {
  AllToHandleType,
  ScreenshotType,
  ToHandleType,
} from "./firebase";
import { url } from "./Server";
import ToHandle from "./ToHandle";
import { UserType } from "./User";

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
        submit={({ old_encrypted, ...data_input }) =>
          encrypt(data_input, props.user, old_encrypted).then((encrypted) =>
            firebase
              .updateToHandle(props.k, {
                data_input,
                encrypted,
              })
              .then(() => props.k)
          )
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
    </>
  );
}

export function encrypt(
  data_input: ScreenshotType,
  user: UserType,
  old_encrypted: string | null
): Promise<string> {
  const body = JSON.stringify({
    ...data_input,
    user,
    old_encrypted,
  });
  delete data_input.params!["cookie"];
  return fetch(`${url}/encrypt`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => Promise.all([Promise.resolve(resp.ok), resp.text()]))
    .then(([ok, text]) => {
      if (!ok) throw Error(text);
      return text;
    });
}

export default Edit;
