import { AllToHandleType, FirebaseWrapper } from "./firebase";
import Home from "./Home";
import { recorded_sha } from "./recorded_sha";

console.log(recorded_sha);
class Main extends FirebaseWrapper<AllToHandleType> {
  getTitle(): string {
    return "first2know";
  }

  getFirebasePath(): string {
    return "/to_handle";
  }

  render() {
    if (this.state === null) return <>Loading...</>;
    return <Home allToHandle={this.state.state} />;
  }
}

export default Main;
