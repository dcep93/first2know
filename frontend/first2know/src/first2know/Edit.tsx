import { Link, useNavigate, useParams } from "react-router-dom";
import firebase, { AllToHandleType, ToHandleType } from "./firebase";
import ToHandle from "./ToHandle";
import { UserType } from "./User";

// TODO dcep93 edit
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
        submit={(data_input) =>
          firebase
            .updateToHandle(props.k, {
              data_input,
              data_output: props.toHandle.data_output,
              user_name: props.user!.screen_name,
              // TODO dcep93 reencrypt
              encrypted: "",
            })
            .then(() => props.k)
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
export default Edit;
