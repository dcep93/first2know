import CreateNew from "./CreateNew";
import { AllToHandleType, FirebaseWrapper } from "./firebase";
import ShowCurrent from "./ShowCurrent";

class Main extends FirebaseWrapper<AllToHandleType> {
  getTitle(): string {
    return "first2know";
  }

  getFirebasePath(): string {
    return "/to_handle";
  }

  render() {
    if (this.state === null) return <>Loading...</>;
    return (
      <>
        <CreateNew />
        <ShowCurrent allToHandle={this.state} />
      </>
    );
    return super.render();
  }
}

export default Main;
