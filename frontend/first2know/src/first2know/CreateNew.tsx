import { createRef, FormEvent, useState } from "react";

const urlRef = createRef<HTMLInputElement>();
const userRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();
const fetchParamsRef = createRef<HTMLInputElement>();

function CreateNew(props: { modalUrl: string }): JSX.Element {
  const [imgData, update] = useState<string | null>(null);
  return (
    <form onSubmit={(e) => checkScreenShot(e, props.modalUrl, update)}>
      <div>
        url: <input ref={urlRef} type="text" />
      </div>
      <div>
        user: <input ref={userRef} type="text" />
      </div>
      <div>
        css_selector: <input ref={cssSelectorRef} type="text" />
      </div>
      <div title={"will be encrypted"}>
        fetch_params: <input ref={fetchParamsRef} type="text" />
      </div>
      <input type="submit" value="Check Screenshot" />
    </form>
  );
}

function checkScreenShot(
  e: FormEvent,
  modalUrl: string,
  update: (imgData: string) => void
) {
  e.preventDefault();
  fetch(`${modalUrl}/screenshot`, { method: "POST" })
    .then((resp) => resp.text())
    .then((text) => console.log(text));
}

export default CreateNew;
