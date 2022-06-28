import { createRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { encrypt } from "./Edit";
import firebase, {
  AllToHandleType,
  ScreenshotType,
  ToHandleType,
} from "./firebase";
import loading from "./loading.gif";

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

type PropsType = {
  toHandle?: ToHandleType;
  submit?: SubmitType;
  allToHandle: AllToHandleType;
};

type UpdateType = (img_data: string | null | undefined) => void;

function ToHandle(props: PropsType) {
  const [img_data, update] = useState<string | null | undefined>(
    props.toHandle?.data_output.img_data
  );
  const navigate = useNavigate();
  const defaultParamsValue = props.toHandle?.data_input.params;
  return (
    <div>
      <form
        onSubmit={(e) => [e.preventDefault(), checkScreenShot(props, update)]}
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
            : img_data === null
            ? loading
            : `data:image/png;base64,${img_data}`
        }
        alt=""
      ></img>
      {props.submit && (
        <button onClick={() => onSubmit(props, navigate, update)}>
          Submit
        </button>
      )}
    </div>
  );
}
function onSubmit(
  props: PropsType,
  navigate: (key: string) => void,
  update: UpdateType
) {
  const old_encrypted = getOldEncrypted(props.toHandle);
  Promise.resolve()
    .then(() => getData(old_encrypted, update, props.allToHandle))
    .then((data_input) => props.submit!({ old_encrypted, ...data_input }))
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
  update: (img_data: string | null | undefined) => void,
  allToHandle: AllToHandleType
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
  return validateScreenshot(data_input, old_encrypted, update, allToHandle);
}

function validateScreenshot(
  data_input: ScreenshotType,
  old_encrypted: string | null,
  update: (img_data: string | null | undefined) => void,
  allToHandle: AllToHandleType
): Promise<ScreenshotType> {
  update(null);
  return encrypt(data_input, null, old_encrypted)
    .then((encrypted) => firebase.pushToHandle(data_input, encrypted, null))
    .then(
      (key) =>
        new Promise((resolve, reject) => {
          // TODO dcep93 listen for changes
          const toHandle = allToHandle[key];
          const data_output = toHandle?.data_output;
          if (data_output) {
            if (data_output.error) reject(data_output.error!.message);
            update(data_output.img_data);
            firebase.deleteToHandle(key).then(() => resolve(data_input));
          }
        })
    )
    .catch((err) => {
      update(undefined);
      alert(err);
      throw err;
    })
    .then((di) => di as ScreenshotType);
}

function checkScreenShot(
  props: PropsType,
  update: (img_data: string | null | undefined) => void
) {
  const old_encrypted = getOldEncrypted(props.toHandle);
  return getData(old_encrypted, update, props.allToHandle);
}

export default ToHandle;
