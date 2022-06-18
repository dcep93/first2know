import { AllToHandleType } from "./firebase";

function ShowCurrent(props: { allToHandle: AllToHandleType }): JSX.Element {
  return <>{JSON.stringify(props.allToHandle, null, 2)}</>;
}

export default ShowCurrent;
