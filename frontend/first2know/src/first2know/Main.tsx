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
    if (this.state === null)
      return <div className="loadingState">Loading first2know…</div>;
    return <Helper toHandles={this.state.state || []} />;
  }
}

function Helper(props: { toHandles: ToHandleType[] }) {
  return (
    <div className="appShell">
      <header className="appHeader">
        <div className="brand">
          <div className="brandMark">f2k</div>
          <div className="brandCopy">
            <strong>first2know</strong>
            <span>Quiet monitoring. Immediate signals.</span>
          </div>
        </div>
        <User />
      </header>
      <main className="appMain">
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
      </main>
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
