import firebase, { ScreenshotType } from "./firebase";

import { url } from "./Server";
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
  return encrypt(data_input, user).then((encrypted) =>
    firebase.pushToHandle({
      data_input,
      data_output: { img_data: "", times: [Date.now()] },
      encrypted,
      user_name: user!.screen_name,
    })
  );
}

function encrypt(data_input: ScreenshotType, user: UserType): Promise<string> {
  const body = JSON.stringify({ ...data_input, user });
  delete data_input.params!["cookie"];
  return fetch(`${url}/encrypt`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => Promise.all([Promise.resolve(resp.ok), resp.text()]))
    .then(([ok, text]) => {
      if (!ok) throw Error(text);
      return text;
    });
}

export default Create;
