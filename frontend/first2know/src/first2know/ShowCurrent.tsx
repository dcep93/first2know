import { AllToHandleType } from "./firebase";

function ShowCurrent(props: { allToHandle: AllToHandleType }) {
  return <>{JSON.stringify(props.allToHandle, null, 2)}</>;
}

export default ShowCurrent;
