import firebase, { DataInputType } from "./firebase";

import ToHandle from "./ToHandle";

function Create(): JSX.Element {
  return <ToHandle submit={(data_input) => submitNew(data_input)} />;
}

function submitNew(data_input: DataInputType): Promise<string> {
  return firebase.pushToHandle(data_input);
}

export default Create;
