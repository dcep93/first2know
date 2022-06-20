import { createRef, FormEvent, useState } from "react";

import loading from "./loading.gif";

const urlRef = createRef<HTMLInputElement>();
const userRef = createRef<HTMLInputElement>();
const cookieRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();

// TODO dcep93 submit
function CreateNew(props: { modalUrl: string }): JSX.Element {
  const [data, update] = useState<string | undefined>(undefined);
  return (
    <div>
      <form onSubmit={(e) => checkScreenShot(e, props.modalUrl, update)}>
        <div>
          url: <input ref={urlRef} type="text" />
        </div>
        <div>
          user: <input ref={userRef} type="text" />
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
          js_evaluate: <input ref={evaluateRef} type="text" />
        </div>
        <input type="submit" value="Check Screenshot" />
      </form>
      <img src={data} alt=""></img>
    </div>
  );
}

function checkScreenShot(
  e: FormEvent,
  modalUrl: string,
  update: (data: string | undefined) => void
) {
  e.preventDefault();
  var params = null;
  if (paramsRef.current!.value !== "") {
    try {
      params = JSON.parse(paramsRef.current!.value);
    } catch (err) {
      alert(err);
      return;
    }
  }
  const data = {
    url: urlRef.current!.value,
    cookie: cookieRef.current!.value || null,
    params,
    evaluate: evaluateRef.current!.value || null,
    selector: cssSelectorRef.current!.value || null,
  };
  const body = JSON.stringify(data);
  update(loading);
  fetch(`${modalUrl}/screenshot_b64`, {
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

export default CreateNew;
