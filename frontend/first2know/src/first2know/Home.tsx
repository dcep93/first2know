import Create from "./Create";
import { AllToHandleType } from "./firebase";
import Show from "./Show";
import { UserType } from "./User";

function Home(props: { user: UserType | null; allToHandle: AllToHandleType }) {
  return (
    <>
      <Create user={props.user} allToHandle={props.allToHandle} />
      <Show allToHandle={props.allToHandle} />
    </>
  );
}

export default Home;
