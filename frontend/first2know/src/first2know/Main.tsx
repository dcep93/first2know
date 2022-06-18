import { AllToHandleType, FirebaseWrapper } from "./firebase";

class Main extends FirebaseWrapper<AllToHandleType> {
  getTitle(): string {
    return "first2know";
  }

  getFirebasePath(): string {
    return "/to_handle";
  }

  render() {
    return super.render();
  }
}

export default Main;
