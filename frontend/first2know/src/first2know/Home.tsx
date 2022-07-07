import Create from "./Create";
import { AllToHandleType, UserType } from "./firebase";
import Show from "./Show";

function Home(props: { user: UserType; allToHandle: AllToHandleType }) {
  return (
    <>
      <Create user={props.user} allToHandle={props.allToHandle} />
      <Show user={props.user} allToHandle={props.allToHandle} />
    </>
  );
}

export default Home;
