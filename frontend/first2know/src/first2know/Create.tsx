import firebase, { ScreenshotType } from "./firebase";

import { url } from "./Server";
import ToHandle, { fetchScreenShot } from "./ToHandle";
import { UserType } from "./User";

function Create(props: { user: UserType }): JSX.Element {
  return (
    <ToHandle
      submit={
        props.user
          ? (data_input) => submitNew(data_input, props.user)
          : undefined
      }
    />
  );
}

function submitNew(
  data_input: ScreenshotType,
  user: UserType
): Promise<string> {
  // fetchScreenShot first to make sure it works
  return fetchScreenShot(data_input).then((img_data) => {
    const payload = JSON.stringify({ ...data_input, user });
    const body = JSON.stringify({ payload });
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
      })
      .then((encrypted) =>
        firebase.pushToHandle({
          data_input,
          data_output: { img_data: "", times: [Date.now()] },
          encrypted,
          user_name: user!.screen_name,
        })
      );
  });
}

export default Create;
