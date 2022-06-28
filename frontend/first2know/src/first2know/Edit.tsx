import { Link, useNavigate, useParams } from "react-router-dom";
import firebase, {
  AllToHandleType,
  ScreenshotType,
  ToHandleType,
} from "./firebase";
import { url } from "./Server";
import ToHandle from "./ToHandle";
import { UserType } from "./User";

function Edit(props: { user: UserType | null; allToHandle: AllToHandleType }) {
  let params = useParams();
  const key = params.key!;
  const toHandle = props.allToHandle[key];
  return (
    <>
      <RoutedEdit k={key} user={props.user} toHandle={toHandle} />
      <div>
        <Link to="/">Home</Link>
      </div>
    </>
  );
}

function RoutedEdit(props: {
  user: UserType | null;
  k: string;
  toHandle: ToHandleType;
}) {
  const navigate = useNavigate();
  if (!props.toHandle) return <pre>key not found: {props.k}</pre>;
  return (
    <>
      <ToHandle
        toHandle={props.toHandle}
        submit={(data_input, { reuse_cookie }) =>
          reencrypt(
            data_input,
            props.user!,
            reuse_cookie ? props.toHandle.encrypted : null
          ).then((encrypted) =>
            firebase
              .updateToHandle(props.k, {
                data_input,
                data_output: props.toHandle.data_output,
                user_name: props.user!.screen_name,
                encrypted,
              })
              .then(() => props.k)
          )
        }
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

function reencrypt(
  data_input: ScreenshotType,
  user: UserType,
  old_encrypted: string | null
): Promise<string> {
  const body = JSON.stringify({
    payload: { ...data_input, user },
    old_encrypted,
  });
  delete data_input.params!["cookie"];
  return fetch(`${url}/reencrypt`, {
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
