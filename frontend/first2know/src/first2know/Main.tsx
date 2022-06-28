import { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Edit from "./Edit";
import { AllToHandleType, FirebaseWrapper } from "./firebase";
import Home from "./Home";
import { recorded_sha } from "./recorded_sha";
import User, { UserType } from "./User";

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

function hashCode(s: string): number {
  var hash = 0;
  for (var i = 0; i < s.length; i++) {
    var code = s.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

function Helper(props: { allToHandle: AllToHandleType }) {
  const [user, update] = useState<UserType>(null);
  const filteredAllToHandle = Object.fromEntries(
    Object.entries(props.allToHandle).filter(
      ([_, toHandle]) =>
        toHandle.user_name === user?.screen_name ||
        hashCode(user?.encrypted || "") === -73599652 // admin
    )
  );
  return (
    <>
      <User user={user} update={update} />
      <BrowserRouter>
        <Routes>
          <Route
            path=":key"
            element={<Edit allToHandle={filteredAllToHandle} />}
          />
          <Route
            index
            element={<Home user={user} allToHandle={filteredAllToHandle} />}
          />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default Main;
