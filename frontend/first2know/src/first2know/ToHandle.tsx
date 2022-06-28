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
const reuseCookieRef = createRef<HTMLInputElement>();

type SubmitType = (
  data_input: ScreenshotType & { old_encrypted: string | null }
) => Promise<string>;

function ToHandle(props: { toHandle?: ToHandleType; submit?: SubmitType }) {
  const [img_data, update] = useState<string | undefined>(
    props.toHandle?.data_output.img_data
  );
  const navigate = useNavigate();
  const defaultParamsValue = props.toHandle?.data_input.params;
  return (
    <div>
      <form
        onSubmit={(e) => [
          e.preventDefault(),
          checkScreenShot(props.toHandle, update),
        ]}
      >
        <div>
          url:{" "}
          <input
            ref={urlRef}
            defaultValue={props.toHandle?.data_input.url}
            type="text"
          />
        </div>
        <div title={"will be encrypted"}>
          cookie: <input ref={cookieRef} type="text" />
        </div>
        {props.toHandle && (
          <div>
            reuse saved cookie?<span> </span>
            <input ref={reuseCookieRef} defaultChecked type="checkbox" />
          </div>
        )}
        <div>
          params:{" "}
          <input
            ref={paramsRef}
            defaultValue={
              defaultParamsValue === null
                ? undefined
                : JSON.stringify(defaultParamsValue)
            }
            type="text"
          />
        </div>
        <div>
          css_selector:{" "}
          <input
            ref={cssSelectorRef}
            defaultValue={props.toHandle?.data_input.selector || undefined}
            type="text"
          />
        </div>
        <div>
          js_evaluate: {"("}transform evaluation to img
          <input
            onChange={() =>
              (cssSelectorRef.current!.disabled =
                evaluationToImgRef.current!.checked)
            }
            defaultChecked={props.toHandle?.data_input.evaluation_to_img}
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
      <img
        src={
          img_data === undefined
            ? undefined
            : `data:image/png;base64,${img_data}`
        }
        alt=""
      ></img>
      {props.submit && (
        <button
          onClick={() =>
            onSubmit(props.toHandle, props.submit!, navigate, update)
          }
        >
          Submit
        </button>
      )}
    </div>
  );
}

function onSubmit(
  toHandle: ToHandleType | undefined,
  submit: SubmitType,
  navigate: (key: string) => void,
  update: (img_data: string | undefined) => void
) {
  const old_encrypted = getOldEncrypted(toHandle);
  Promise.resolve()
    .then(() => getData(old_encrypted, update))
    .then((data_input) => submit({ old_encrypted, ...data_input }))
    .then((key) => navigate(key))
    .catch((err) => {
      alert(err);
      throw err;
    });
}

function getOldEncrypted(toHandle: ToHandleType | undefined) {
  return toHandle === undefined
    ? null
    : reuseCookieRef.current?.checked
    ? toHandle.encrypted
    : null;
}

function getData(
  old_encrypted: string | null,
  update: (img_data: string | undefined) => void
): Promise<ScreenshotType> {
  const paramsJson = paramsRef.current!.value || null;
  const params = paramsJson ? JSON.parse(paramsJson) : {};
  const cookie = cookieRef.current!.value || null;
  if (cookie) params.cookie = cookie;
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
  return validateScreenshot(data_input, old_encrypted, update);
}

// TODO dcep93 have cron respond!
function validateScreenshot(
  data_input: ScreenshotType,
  old_encrypted: string | null,
  update: (img_data: string | undefined) => void
): Promise<ScreenshotType> {
  const body = JSON.stringify({
    ...data_input,
    old_encrypted,
  });
  update(loading);
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
    .then((json) => [json.img_data, console.log(json.evaluate)][0])
    .then((img_data) => [data_input, update(img_data)][0]!)
    .catch((err) => {
      update(undefined);
      alert(err);
      throw err;
    });
}

function checkScreenShot(
  toHandle: ToHandleType | undefined,
  update: (img_data: string | undefined) => void
) {
  const old_encrypted = getOldEncrypted(toHandle);
  return getData(old_encrypted, update);
}

export default ToHandle;
