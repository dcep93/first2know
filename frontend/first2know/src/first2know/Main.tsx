import CreateNew from "./CreateNew";
import { AllToHandleType, FirebaseWrapper } from "./firebase";
import ShowCurrent from "./ShowCurrent";

const modalUrl = "https://dcep93-first2know-app.modal.run";
fetch(modalUrl)
  .then((resp) => resp.text())
  .then((text) => console.log(text));

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
        <CreateNew modalUrl={modalUrl} />
        <ShowCurrent allToHandle={this.state.state} />
      </>
    );
  }
}

export default Main;
