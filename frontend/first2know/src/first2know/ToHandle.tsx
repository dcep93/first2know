import { createRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AllToHandleType,
  DataInputType,
  ToHandleType,
  UserType,
} from "./firebase";
import loading from "./loading.gif";
import { sfetch, url } from "./Server";

const urlRef = createRef<HTMLInputElement>();
const cookieRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const evaluationToImgRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();
const reuseCookieRef = createRef<HTMLInputElement>();

type SubmitType = (
  data_input: DataInputType & { old_encrypted: string | null }
) => Promise<string>;

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
      <button
        onClick={() =>
          Promise.resolve()
            .then(() => getData(props.toHandle))
            .then((data_input) => props.submit(data_input))
            .then((key) => navigate(`/${key}`))
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
            .then(() => getData(props.toHandle))
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
            .then((json) => update(json.img_data))
            .catch((err) => {
              update(undefined);
              alert(err);
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
            : `data:image/png;base64,${img_data}`
        }
        alt=""
      ></img>
    </div>
  );
}

function getData(
  toHandle: ToHandleType | undefined
): DataInputType & { old_encrypted: string | null } {
  const old_encrypted =
    toHandle === undefined
      ? null
      : reuseCookieRef.current?.checked
      ? toHandle.encrypted
      : null;
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
    evaluation_to_img: evaluationToImgRef.current!.checked || null,
  };
  if (data_input.url === "") {
    throw Error("need to have a url");
  }
  return { old_encrypted, ...data_input };
}

export default ToHandle;
