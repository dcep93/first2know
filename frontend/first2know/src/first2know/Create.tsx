import firebase, { ScreenshotType } from "./firebase";

import { url } from "./Server";
import ToHandle from "./ToHandle";
import { UserType } from "./User";

function Create(props: { user: UserType }): JSX.Element {
  return (
    <ToHandle
      submit={props.user ? (data) => submitNew(data, props.user) : undefined}
    />
  );
}

function submitNew(data: ScreenshotType, user: UserType): Promise<string> {
  const payload = JSON.stringify({ ...data, user });
  const body = JSON.stringify({ payload });
  delete data.params!["cookie"];
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
        ...data,
        encrypted,
        user_name: user!.screen_name,
      })
    );
}

export default Create;
