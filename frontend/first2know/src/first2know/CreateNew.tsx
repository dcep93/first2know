import { createRef, useState } from "react";
import firebase from "./firebase";

import loading from "./loading.gif";

const urlRef = createRef<HTMLInputElement>();
const userRef = createRef<HTMLInputElement>();
const cookieRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const cssSelectorRef = createRef<HTMLInputElement>();

function CreateNew(props: { modalUrl: string }): JSX.Element {
  const [data, update] = useState<string | undefined>(undefined);
  return (
    <div>
      <div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            checkScreenShot(props.modalUrl, update);
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
            submitNew(props.modalUrl);
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

function getData() {
  var params = null;
  if (paramsRef.current!.value !== "") {
    params = JSON.parse(paramsRef.current!.value);
  }
  return {
    url: urlRef.current!.value,
    cookie: cookieRef.current!.value || null,
    params,
    evaluate: evaluateRef.current!.value || null,
    selector: cssSelectorRef.current!.value || null,
  };
}

function checkScreenShot(
  modalUrl: string,
  update: (data: string | undefined) => void
) {
  var data;
  try {
    data = getData();
  } catch (err) {
    alert(err);
    return;
  }
  const body = JSON.stringify(data);
  update(loading);
  fetch(`${modalUrl}/screenshot`, {
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

function submitNew(modalUrl: string) {
  var data: any;
  try {
    data = getData();
  } catch (err) {
    alert(err);
    return;
  }
  var p;
  // TODO dcep93 hash with url
  if (data.cookie !== null) {
    p = fetch(`${modalUrl}/encrypt/${data.cookie}`)
      .then((resp) => resp.text())
      .then((e_cookie) => Object.assign(data, { cookie: null, e_cookie }));
  } else {
    p = Promise.resolve(data);
  }
  p.then((data) => {
    Object.assign(data, { user: userRef.current!.value });
    firebase.pushToHandle(data);
  });
}

export default CreateNew;
