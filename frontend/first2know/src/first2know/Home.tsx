import Create from "./Create";
import { ToHandleType } from "./firebase";
import Show from "./Show";

function Home(props: { toHandles: ToHandleType[] }) {
  return (
    <>
      <Create />
      <Show {...props} />
    </>
  );
}

export default Home;
