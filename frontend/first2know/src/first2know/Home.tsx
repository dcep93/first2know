import Create from "./Create";
import { AllToHandleType } from "./firebase";
import Show from "./Show";
import { UserType } from "./User";

function Home(props: { user: UserType; allToHandle: AllToHandleType }) {
  return (
    <>
      <Create user={props.user} allToHandle={props.allToHandle} />
      <Show user={props.user} allToHandle={props.allToHandle} />
    </>
  );
}

export default Home;
