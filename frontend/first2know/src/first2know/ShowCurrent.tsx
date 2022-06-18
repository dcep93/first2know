import { AllToHandleType } from "./firebase";

// TODO dcep93 implement
function ShowCurrent(props: { allToHandle: AllToHandleType }): JSX.Element {
  return <pre>{JSON.stringify(props.allToHandle, null, 2)}</pre>;
}

export default ShowCurrent;
