import { createRef, useState } from "react";
import firebase, { ScreenshotType } from "./firebase";

import loading from "./loading.gif";
import { UserType } from "./Login";
import { url } from "./Server";

const urlRef = createRef<HTMLInputElement>();
const cookieRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const cssSelectorRef = createRef<HTMLInputElement>();

function CreateNew(props: { user: UserType }): JSX.Element {
  const [data, update] = useState<string | undefined>(undefined);
  return (
    <div>
      <div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            checkScreenShot(update);
          }}
        >
          <div>
            url: <input ref={urlRef} type="text" />
          </div>
          <div title={"will be encrypted"}>
            cookie: <input ref={cookieRef} type="text" />
          </div>
          <div>
            params: <input ref={paramsRef} type="text" />
          </div>
          <div>
            css_selector: <input ref={cssSelectorRef} type="text" />
          </div>
          <div>
            js_evaluate:
            <div>
              <textarea ref={evaluateRef} />
            </div>
          </div>
          <input type="submit" value="Check Screenshot" />
        </form>
      </div>
      {props.user && (
        <div>
          <form onSubmit={(e) => [e.preventDefault(), submitNew(props.user!)]}>
            <input type="submit" value="Submit" />
          </form>
        </div>
      )}
      <img src={data} alt=""></img>
    </div>
  );
}

function getData(): ScreenshotType {
  const paramsJson = paramsRef.current!.value || null;
  var params;
  if (paramsJson) {
    try {
      params = JSON.parse(paramsJson);
    } catch (err) {
      alert(err);
      throw err;
    }
  } else {
    params = {};
  }
  Object.assign(params, { cookie: cookieRef.current!.value || null });
  return {
    url: urlRef.current!.value,
    params,
    evaluate: evaluateRef.current!.value || null,
    selector: cssSelectorRef.current!.value || null,
  };
}

function checkScreenShot(update: (data: string | undefined) => void) {
  const data = getData();
  const body = JSON.stringify(data);
  update(loading);
  fetch(`${url}/screenshot`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => Promise.all([Promise.resolve(resp), resp.text()]))
    .then(([resp, text]) => {
      if (!resp.ok) throw Error(text);
      return text;
    })
    .then((text) => JSON.parse(text))
    .then((json) => [console.log(json.evaluate), json.data])
    .then(([_, bytes]) => `data:image/png;base64,${bytes}`)
    .then(update)
    .catch((err) => {
      update(undefined);
      const e: string = err.toString();
      alert(e.substring(e.length - 1000));
      throw err;
    });
}

function submitNew(user: UserType) {
  const data = getData();
  const payload = { ...data, user };
  const body = JSON.stringify({ payload });
  delete data.params!["cookie"];
  fetch(`${url}/encrypt`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => resp.text())
    .then((encrypted) =>
      firebase.pushToHandle({
        ...data,
        encrypted,
        user_name: user!.screen_name,
      })
    );
}

export default CreateNew;
