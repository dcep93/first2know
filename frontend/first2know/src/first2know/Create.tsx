import firebase, { DataInputType } from "./firebase";

import ToHandle from "./ToHandle";

function Create(): JSX.Element {
  return (
    <ToHandle
      submit={(data_input, disabled) => submitNew(data_input, disabled)}
    />
  );
}

function submitNew(
  data_input: DataInputType,
  disabled: boolean | null
): Promise<string> {
  return firebase.pushToHandle(data_input, disabled);
}

export default Create;
