import firebase, { AllToHandleType, DataInputType } from "./firebase";

import ToHandle from "./ToHandle";

function Create(props: {
  user: string;
  allToHandle: AllToHandleType;
}): JSX.Element {
  return (
    <>
      <ToHandle
        user={props.user}
        submit={(data_input) => submitNew(data_input, props.user!)}
        allToHandle={props.allToHandle}
      />
    </>
  );
}

function submitNew(data_input: DataInputType, user: string): Promise<string> {
  return firebase.pushToHandle(data_input, user);
}

export default Create;
