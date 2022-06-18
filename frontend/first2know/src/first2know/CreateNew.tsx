import { createRef, FormEvent, useState } from "react";

const urlRef = createRef<HTMLInputElement>();
const userRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();
const fetchParamsRef = createRef<HTMLInputElement>();

// TODO dcep93 submit
function CreateNew(props: { modalUrl: string }): JSX.Element {
  const [imgData, update] = useState<string | undefined>(undefined);
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
      <img src={imgData}></img>
    </div>
  );
}

// TODO dcep93 loading
function checkScreenShot(
  e: FormEvent,
  modalUrl: string,
  update: (imgData: string) => void
) {
  e.preventDefault();
  const data = { url: "https://chess.com" };
  const body = JSON.stringify(data);
  fetch(`${modalUrl}/screenshot_b64`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => resp.text())
    .then((bytes) => `data:image/png;base64,${bytes}`)
    .then(update);
}

export default CreateNew;
