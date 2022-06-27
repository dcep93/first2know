import { useState } from "react";
import CreateNew from "./CreateNew";
import { AllToHandleType, FirebaseWrapper } from "./firebase";
import Login, { UserType } from "./Login";
import { recorded_sha } from "./recorded_sha";
import ShowCurrent from "./ShowCurrent";

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
      <Login user={user} update={update} />
      <CreateNew user={user} />
      <ShowCurrent user={user} allToHandle={props.allToHandle} />
    </>
  );
}

export default Main;
