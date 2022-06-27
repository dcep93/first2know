import { useState } from "react";
import Create from "./Create";
import { AllToHandleType } from "./firebase";
import Show from "./Show";
import User, { UserType } from "./User";

function Home(props: { allToHandle: AllToHandleType }) {
  const [user, update] = useState<UserType>(null);
  return (
    <>
      <User user={user} update={update} />
      <Create user={user} />
      <Show user={user} allToHandle={props.allToHandle} />
    </>
  );
}

export default Home;
