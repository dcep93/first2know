import { createRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clog, url } from "./Server";
import { DataInputType, ScreenshotDataType, ToHandleType } from "./firebase";
import loading from "./loading.gif";

const urlRef = createRef<HTMLInputElement>();
const rawProxyRef = createRef<HTMLInputElement>();
const cookiesRef = createRef<HTMLInputElement>();
const userAgentRef = createRef<HTMLInputElement>();
const paramsRef = createRef<HTMLInputElement>();
const evaluateRef = createRef<HTMLTextAreaElement>();
const evaluationToImgRef = createRef<HTMLInputElement>();
const cssSelectorRef = createRef<HTMLInputElement>();

type SubmitType = (data_input: DataInputType) => Promise<string>;

function ToHandle(props: { toHandle?: ToHandleType; submit: SubmitType }) {
  const [resp_data, update] = useState<
    (ScreenshotDataType & { err?: string }) | null | undefined
  >(undefined);
  const navigate = useNavigate();

  const defaultParamsValue = props.toHandle?.data_input.params;
  const defaultCookiesValue = props.toHandle?.data_input.cookies;
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
              fetch(`${url}/screenshot`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body,
              })
            )
            .then((resp) => resp.json())
            .then(clog)
            .then((resp_data: any) =>
              resp_data.err ? Promise.reject(resp_data.err) : update(resp_data)
            )
            .catch((err) => {
              update({ err: `${err}` } as any);
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
          cookies:{" "}
          <input
            ref={cookiesRef}
            defaultValue={
              defaultCookiesValue === null
                ? undefined
                : JSON.stringify(defaultCookiesValue)
            }
            type="text"
          />
        </div>
        <div>
          css_selector:{" "}
          <input
            ref={cssSelectorRef}
            disabled={props.toHandle?.data_input.evaluation_to_img || false}
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
              style={{ width: "40em", height: "10em" }}
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
          ) : resp_data.err ? (
            <pre>{resp_data.err}</pre>
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
  const params = paramsJson ? JSON.parse(paramsJson) : null;
  const cookiesJson = cookiesRef.current!.value || null;
  const cookies = cookiesJson ? JSON.parse(cookiesJson) : null;
  return {
    url: urlRef.current!.value,
    params,
    cookies,
    selector: cssSelectorRef.current!.value || null,
    evaluate: evaluateRef.current!.value || null,
    evaluation_to_img: evaluationToImgRef.current!.checked || null,
    user_agent_hack: userAgentRef.current!.checked || null,
    raw_proxy: rawProxyRef.current!.checked || null,
  };
}

export default ToHandle;
