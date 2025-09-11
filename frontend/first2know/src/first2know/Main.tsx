import { BrowserRouter, Route, Routes, useParams } from "react-router-dom";
import Edit from "./Edit";
import { FirebaseWrapper, ToHandleType } from "./firebase";
import Home from "./Home";
import { recorded_sha } from "./recorded_sha";
import Server from "./Server";
import User, { LOCAL_USER } from "./User";

console.log(recorded_sha);

class Main extends FirebaseWrapper<ToHandleType[]> {
  getTitle(): string {
    return "first2know";
  }

  getFirebasePath(): string {
    return "/to_handle";
  }

  render() {
    if (this.state === null) return <>Loading...</>;
    return <Helper toHandles={this.state.state || []} />;
  }
}

function Helper(props: { toHandles: ToHandleType[] }) {
  return (
    <div>
      <User />
      {LOCAL_USER && (
        <BrowserRouter>
          <Routes>
            <Route
              path=":key"
              element={<MainRoutedEdit toHandles={props.toHandles} />}
            />
            <Route index element={<Home toHandles={props.toHandles} />} />
          </Routes>
        </BrowserRouter>
      )}
      <Server />
    </div>
  );
}

function MainRoutedEdit(props: { toHandles: ToHandleType[] }) {
  let params = useParams();
  const toHandle = props.toHandles.find(
    (toHandle) => toHandle.key === params.key
  );
  if (!toHandle) return <pre>key not found: {params.key}</pre>;
  return <Edit toHandle={toHandle} />;
}

export default Main;
