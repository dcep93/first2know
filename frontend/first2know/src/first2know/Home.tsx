import Create from "./Create";
import { AllToHandleType } from "./firebase";
import Show from "./Show";
import { UserType } from "./User";

function Home(props: { user: UserType; allToHandle: AllToHandleType }) {
  return (
    <>
      <Create user={props.user} />
      <Show allToHandle={props.allToHandle} />
    </>
  );
}

export default Home;
