import { useState } from "react";
import { BrowserRouter, Route, Routes, useParams } from "react-router-dom";
import Edit from "./Edit";
import { AllToHandleType, FirebaseWrapper, UserType } from "./firebase";
import Home from "./Home";
import { recorded_sha } from "./recorded_sha";
import Server from "./Server";
import User, { isAdmin } from "./User";

console.log(recorded_sha);

class Main extends FirebaseWrapper<AllToHandleType> {
  getTitle(): string {
    return "first2know";
  }

  getFirebasePath(): string {
    return "/to_handle";
  }

  render() {
    if (this.state === null) return <>Loading...</>;
    const allToHandle = this.state.state || {};
    return <Helper allToHandle={allToHandle} />;
  }
}

function Helper(props: { allToHandle: AllToHandleType }) {
  const local = localStorage.getItem("login");
  var u = null;
  if (local) {
    u = JSON.parse(local);
  }

  const [user, update] = useState<UserType | null>(u);
  const filteredAllToHandle = Object.fromEntries(
    Object.entries(props.allToHandle).filter(
      ([_, toHandle]) =>
        toHandle.user.email === user?.email || (user && isAdmin(user))
    )
  );
  return (
    <div>
      <User user={user} update={update} />
      {user && (
        <BrowserRouter>
          <Routes>
            <Route
              path=":key"
              element={
                <RoutedEdit user={user} allToHandle={filteredAllToHandle} />
              }
            />
            <Route
              index
              element={<Home user={user} allToHandle={filteredAllToHandle} />}
            />
          </Routes>
        </BrowserRouter>
      )}
      <Server />
    </div>
  );
}

function RoutedEdit(props: { user: UserType; allToHandle: AllToHandleType }) {
  let params = useParams();
  const k = params.key!;
  return <Edit k={k} user={props.user} allToHandle={props.allToHandle} />;
}

export default Main;
