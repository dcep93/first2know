import { createRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clog, sfetch, url } from "./Server";
import {
  AllToHandleType,
  DataInputType,
  ScreenshotDataType,
  ToHandleType,
  UserType,
} from "./firebase";
import loading from "./loading.gif";

const urlRef = createRef<HTMLInputElement>();
const rawProxyRef = createRef<HTMLInputElement>();
// const cookieRef = createRef<HTMLInputElement>();
const userAgentRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const evaluationToImgRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();
// const deleteOldCookieRef = createRef<HTMLInputElement>();

type SubmitType = (data_input: DataInputType) => Promise<string>;

function ToHandle(props: {
  user: UserType;
  toHandle?: ToHandleType;
  submit: SubmitType;
  allToHandle: AllToHandleType;
}) {
  const [resp_data, update] = useState<ScreenshotDataType | null | undefined>(
    undefined
  );
  const navigate = useNavigate();

  const defaultParamsValue = props.toHandle?.data_input.params;
  return (
    <div>
      <button
        onClick={() =>
          Promise.resolve()
            .then(() => getData())
            .then((data_input) => props.submit(data_input))
            .then((key) =>
              props.toHandle ? alert("success") : navigate(`/${key}`)
            )
            .catch((err) => {
              alert(err);
              throw err;
            })
        }
      >
        Submit
      </button>
      <form
        onSubmit={(e) =>
          Promise.resolve(e.preventDefault())
            .then(() => update(null))
            .then(() => getData())
            .then((data_input) => ({
              evaluation:
                props.toHandle?.data_output?.screenshot_data?.evaluation ||
                null,
              ...data_input,
            }))
            .then((data) => JSON.stringify(data))
            .then((body) =>
              sfetch(`${url}/screenshot`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body,
              })
            )
            .then((resp) => resp.json())
            .then(clog)
            .then((resp_data: ScreenshotDataType) => update(resp_data))
            .catch((err) => {
              update(undefined);
              const e = `${err}`;
              alert(e.slice(Math.max(0, e.length - 1000)));
              throw err;
            })
        }
      >
        <div>
          url:{" "}
          <input
            ref={urlRef}
            defaultValue={props.toHandle?.data_input.url}
            type="text"
          />
        </div>
        <div>
          raw proxy ?
          <input
            ref={rawProxyRef}
            defaultChecked={props.toHandle?.data_input.raw_proxy || false}
            type="checkbox"
          />
        </div>
        {/* <div title={"will be encrypted"}>
          cookie: <input ref={cookieRef} type="text" />
        </div>
        {props.toHandle && (
          <div>
            delete old cookie?
            <input ref={deleteOldCookieRef} type="checkbox" />
          </div>
        )} */}
        <div>
          user agent hack:{" "}
          <input
            ref={userAgentRef}
            defaultChecked={props.toHandle?.data_input.user_agent_hack || false}
            type="checkbox"
          />
        </div>
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
            defaultChecked={
              props.toHandle?.data_input.evaluation_to_img || false
            }
            ref={evaluationToImgRef}
            type="checkbox"
          />
          {")"}
          <div>
            <textarea
              defaultValue={props.toHandle?.data_input.evaluate || undefined}
              ref={evaluateRef}
            />
          </div>
        </div>
        <input type="submit" value="Check Screenshot" />
      </form>
      <div>
        <div>
          {resp_data === undefined ? undefined : resp_data === null ? (
            <img src={loading} alt="" />
          ) : (
            <div>
              <img src={`data:image/png;base64,${resp_data.img_data}`} alt="" />
              <div>
                <pre>
                  {JSON.stringify(
                    { ...resp_data, img_data: undefined },
                    null,
                    2
                  )}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getData(): DataInputType {
  const paramsJson = paramsRef.current!.value || null;
  const params = paramsJson ? JSON.parse(paramsJson) : {};
  // const cookie = cookieRef.current!.value || null;
  // if (cookie) params.cookie = cookie;
  return {
    url: urlRef.current!.value,
    params,
    selector: cssSelectorRef.current!.value || null,
    evaluate: evaluateRef.current!.value || null,
    evaluation_to_img: evaluationToImgRef.current!.checked || false,
    user_agent_hack: userAgentRef.current!.checked || null,
    raw_proxy: rawProxyRef.current!.checked || null,
  };
}

export default ToHandle;
