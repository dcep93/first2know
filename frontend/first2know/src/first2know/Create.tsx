import { encrypt } from "./Edit";
import firebase, { ScreenshotType } from "./firebase";

import ToHandle from "./ToHandle";
import { UserType } from "./User";

function Create(props: { user: UserType | null }): JSX.Element {
  return (
    <ToHandle
      submit={
        props.user
          ? (data_input) => submitNew(data_input, props.user!)
          : undefined
      }
    />
  );
}

function submitNew(
  data_input: ScreenshotType,
  user: UserType
): Promise<string> {
  return encrypt(data_input, user, null).then((encrypted) =>
    firebase.pushToHandle(data_input, encrypted, user!.screen_name)
  );
}

export default Create;
