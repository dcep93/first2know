import { createRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ScreenshotType, ToHandleType } from "./firebase";
import loading from "./loading.gif";
import { url } from "./Server";

const urlRef = createRef<HTMLInputElement>();
const cookieRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const evaluationToImgRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();

function ToHandle(props: {
  toHandle?: ToHandleType;
  submit?: (s: ScreenshotType) => Promise<string>;
}) {
  const [data, update] = useState<string | undefined>(undefined);
  const navigate = useNavigate();
  return (
    <div>
      <form onSubmit={(e) => [e.preventDefault(), checkScreenShot(update)]}>
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
          js_evaluate: {"("}transform evaluation to img
          <input
            onChange={() =>
              (cssSelectorRef.current!.disabled =
                evaluationToImgRef.current!.checked)
            }
            ref={evaluationToImgRef}
            type="checkbox"
          />
          {")"}
          <div>
            <textarea ref={evaluateRef} />
          </div>
        </div>
        <input type="submit" value="Check Screenshot" />
      </form>
      <img src={data} alt=""></img>
      {props.submit && (
        <button
          onClick={() =>
            Promise.resolve()
              .then(() => getData())
              .then((data) => props.submit!(data))
              .then((key) => navigate(key))
              .catch((err) => {
                alert(err);
                throw err;
              })
          }
        >
          Submit
        </button>
      )}
    </div>
  );
}

function getData(): ScreenshotType {
  const paramsJson = paramsRef.current!.value || null;
  const params = paramsJson ? JSON.parse(paramsJson) : {};
  Object.assign(params, { cookie: cookieRef.current!.value || null });
  const rval = {
    url: urlRef.current!.value,
    params,
    selector: cssSelectorRef.current!.value || null,
    evaluation: null,
    evaluate: evaluateRef.current!.value || null,
    evaluation_to_img: evaluationToImgRef.current!.checked,
  };
  if (rval.url === "") {
    throw "need to have a url";
  }
  return rval;
}

function checkScreenShot(update: (data: string | undefined) => void) {
  const data = getData();
  update(loading);
  return fetchScreenShot(data)
    .then((bytes) => `data:image/png;base64,${bytes}`)
    .then(update)
    .catch((err) => {
      update(undefined);
      throw err;
    });
}

export function fetchScreenShot(data_input: ScreenshotType): Promise<string> {
  const body = JSON.stringify(data_input);
  return fetch(`${url}/screenshot`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body,
  })
    .then((resp) => Promise.all([Promise.resolve(resp.ok), resp.text()]))
    .then(([ok, text]) => {
      if (!ok) throw Error(text.substring(text.length - 1000));
      return text;
    })
    .then((text) => JSON.parse(text))
    .then((json) => [json.img_data, console.log(json.evaluate)][0]);
}

export default ToHandle;
