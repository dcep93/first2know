import { createRef, useState } from "react";
import firebase, { ToHandleType } from "./firebase";

import loading from "./loading.gif";
import { url } from "./Server";

const urlRef = createRef<HTMLInputElement>();
const userRef = createRef<HTMLInputElement>();
const cookieRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const cssSelectorRef = createRef<HTMLInputElement>();

function CreateNew(): JSX.Element {
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
      <div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitNew();
          }}
        >
          <div>
            user: <input ref={userRef} type="text" />
          </div>
          <input type="submit" value="Submit" />
        </form>
      </div>
      <img src={data} alt=""></img>
    </div>
  );
}

function getData(): ToHandleType {
  return {
    user: null,
    url: urlRef.current!.value,
    evaluate: evaluateRef.current!.value || null,
    selector: cssSelectorRef.current!.value || null,
  };
}

function checkScreenShot(update: (data: string | undefined) => void) {
  var data;
  try {
    data = getData();
  } catch (err) {
    alert(err);
    return;
  }
  var params =
    paramsRef.current!.value === "" ? {} : JSON.parse(paramsRef.current!.value);
  Object.assign(params, { cookie: cookieRef.current!.value || null });
  Object.assign(data, { params });
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
    .then((json) => {
      console.log(json.evaluate);
      return json.data;
    })
    .then((bytes) => `data:image/png;base64,${bytes}`)
    .then(update)
    .catch((err) => {
      update(undefined);
      const e: string = err.toString();
      alert(e.substring(e.length - 1000));
      throw err;
    });
}

function submitNew() {
  var data: any;
  try {
    data = getData();
  } catch (err) {
    alert(err);
    return;
  }
  Object.assign(data, {
    user: userRef.current!.value,
    params: paramsRef.current!.value,
  });
  var p;
  if (data.cookie !== null) {
    const body = JSON.stringify(data);
    p = fetch(`${url}/encrypt`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    })
      .then((resp) => resp.text())
      .then((e_cookie) => Object.assign(data, { cookie: null, e_cookie }));
  } else {
    p = Promise.resolve(data);
  }
  p.then((data) => firebase.pushToHandle(data));
}

export default CreateNew;
