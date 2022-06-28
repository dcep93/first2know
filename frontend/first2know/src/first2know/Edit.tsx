import { useNavigate, useParams } from "react-router-dom";
import firebase, { AllToHandleType, ToHandleType } from "./firebase";

// TODO dcep93 edit
// todo can only edit your own
function Edit(props: { allToHandle: AllToHandleType }) {
  let params = useParams();
  const key = params.key!;
  const toHandle = props.allToHandle[key];
  if (!toHandle) return <pre>key not found: {key}</pre>;
  return <RoutedEdit k={key} toHandle={toHandle} />;
}

function RoutedEdit(props: { k: string; toHandle: ToHandleType }) {
  const navigate = useNavigate();
  return (
    <>
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
