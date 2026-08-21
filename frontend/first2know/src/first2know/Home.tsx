import Create from "./Create";
import { ToHandleType } from "./firebase";
import Show from "./Show";

function Home(props: { toHandles: ToHandleType[] }) {
  return (
    <div className="pageStack">
      <section>
        <div className="sectionHeading">
          <div>
            <h1>New monitor</h1>
            <p>Create, preview, and schedule a new signal.</p>
          </div>
        </div>
        <Create />
      </section>
      <section>
        <div className="sectionHeading">
          <div>
            <h2>Monitors</h2>
            <p>Every encrypted job remains visible below.</p>
          </div>
          <span className="countPill">{props.toHandles.length} total</span>
        </div>
        <Show {...props} />
      </section>
    </div>
  );
}

export default Home;
