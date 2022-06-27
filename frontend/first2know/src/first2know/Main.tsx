import { useState } from "react";
import Create from "./Create";
import { AllToHandleType, FirebaseWrapper } from "./firebase";
import { recorded_sha } from "./recorded_sha";
import Show from "./Show";
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
    return <SubFirebase allToHandle={this.state.state} />;
  }
}

function SubFirebase(props: { allToHandle: AllToHandleType }) {
  const [user, update] = useState<UserType>(null);
  return (
    <>
      <User user={user} update={update} />
      <Create user={user} />
      <Show user={user} allToHandle={props.allToHandle} />
    </>
  );
}

export default Main;
