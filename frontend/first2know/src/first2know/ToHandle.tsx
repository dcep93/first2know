import { createRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { sfetch, url } from "./Server";
import {
  AllToHandleType,
  DataInputType,
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
  const [img_data, update] = useState<string | null | undefined>(undefined);
  const navigate = useNavigate();

  const defaultParamsValue = props.toHandle?.data_input.params;
  return (
    <div>
      <img
        src="data:image/png;base64,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"
        alt="Embedded Image"
      />

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
            .then((json) => update(`data:image/png;base64,${json.img_data}`))
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
      <img
        src={
          img_data === undefined
            ? undefined
            : img_data === null
            ? loading
            : img_data
        }
        alt=""
      ></img>
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
