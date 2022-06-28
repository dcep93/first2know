import { BrowserRouter, Route, Routes } from "react-router-dom";
import Edit from "./Edit";
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
    const allToHandle = this.state.state || {};
    return (
      <BrowserRouter>
        <Routes>
          <Route path=":key" element={<Edit allToHandle={allToHandle} />} />
          <Route index element={<Home allToHandle={allToHandle} />} />
        </Routes>
      </BrowserRouter>
    );
  }
}

export default Main;
