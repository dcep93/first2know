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

// TODO dcep93 edit
function ToHandle(props: {
  toHandle?: ToHandleType;
  submit?: (data_input: ScreenshotType, img_data: string) => Promise<string>;
}) {
  const [img_data, update] = useState<string | undefined>(undefined);
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
      <img src={img_data} alt=""></img>
      {props.submit && (
        <button
          onClick={() =>
            Promise.resolve()
              .then(() => getData())
              .then(({ img_data, ...data_input }) =>
                props.submit!(data_input, img_data)
              )
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

function getData(): Promise<ScreenshotType & { img_data: string }> {
  const paramsJson = paramsRef.current!.value || null;
  const params = paramsJson ? JSON.parse(paramsJson) : {};
  params.cookie = cookieRef.current!.value || null;
  const data_input = {
    url: urlRef.current!.value,
    params,
    selector: cssSelectorRef.current!.value || null,
    evaluation: null,
    evaluate: evaluateRef.current!.value || null,
    evaluation_to_img: evaluationToImgRef.current!.checked,
  };
  if (data_input.url === "") {
    throw Error("need to have a url");
  }
  // always fetch screenshot
  // to validate the payload
  return fetchScreenShot(data_input).then((img_data) => ({
    img_data,
    ...data_input,
  }));
}

function fetchScreenShot(data_input: ScreenshotType): Promise<string> {
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

function checkScreenShot(update: (img_data: string | undefined) => void) {
  update(loading);
  return getData()
    .then(({ img_data }) => `data:image/png;base64,${img_data}`)
    .then(update)
    .catch((err) => {
      update(undefined);
      throw err;
    });
}

export default ToHandle;
