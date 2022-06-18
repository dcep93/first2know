import { createRef, FormEvent, useState } from "react";

import loading from "./loading.gif";

const urlRef = createRef<HTMLInputElement>();
const userRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();
const fetchParamsRef = createRef<HTMLInputElement>();

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
        <div>
          selector: <input ref={cssSelectorRef} type="text" />
        </div>
        <div title={"will be encrypted"}>
          fetch_params: <input ref={fetchParamsRef} type="text" />
        </div>
        <input type="submit" value="Check Screenshot" />
      </form>
      <img src={data} alt=""></img>
    </div>
  );
}

// TODO dcep93 loading
function checkScreenShot(
  e: FormEvent,
  modalUrl: string,
  update: (data: string | undefined) => void
) {
  e.preventDefault();
  const data = { url: urlRef.current!.value };
  const body = JSON.stringify(data);
  update(loading);
  fetch(`${modalUrl}/screenshot_b64`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => resp.text())
    .then((bytes) => `data:image/png;base64,${bytes}`)
    .then(update)
    .catch((err) => {
      update(undefined);
      throw err;
    });
}

export default CreateNew;
