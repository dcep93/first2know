import Create from "./Create";
import { AllToHandleType } from "./firebase";
import Show from "./Show";

function Home(props: { user: string; allToHandle: AllToHandleType }) {
  return (
    <>
      <Create user={props.user} allToHandle={props.allToHandle} />
      <Show user={props.user} allToHandle={props.allToHandle} />
    </>
  );
}

export default Home;
