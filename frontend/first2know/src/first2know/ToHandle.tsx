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
const disabledRef = createRef<HTMLInputElement>();

type SubmitType = (
  data_input: DataInputType,
  disabled: boolean | null
) => Promise<string>;

function ToHandle(props: { toHandle?: ToHandleType; submit: SubmitType }) {
  const [resp_data, update] = useState<
    (ScreenshotDataType & { err?: string }) | null | undefined
  >(undefined);
  const navigate = useNavigate();

  const defaultParamsValue = props.toHandle?.data_input.params;
  const defaultCookiesValue = props.toHandle?.data_input.cookies;
  return (
    <section className="editorCard">
      <header className="editorHeading">
        <div>
          <h2>{props.toHandle ? "Edit monitor" : "Monitor details"}</h2>
          <p>
            {props.toHandle
              ? props.toHandle.key
              : "Configure every request and notification option."}
          </p>
        </div>
        <span
          className={`statusPill ${
            props.toHandle?.disabled
              ? "statusPillDisabled"
              : "statusPillOnline"
          }`}
        >
          {props.toHandle?.disabled ? "Disabled" : "Active"}
        </span>
      </header>
      <div className="editorBody">
        <div className="topActions">
          <button
            onClick={() =>
              Promise.resolve()
                .then(() => props.submit(getData(), getDisabled()))
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
        </div>

        <div className="toggleGrid">
          <label className="toggleControl">
            <span>Disabled</span>
            <input
              ref={disabledRef}
              defaultChecked={props.toHandle?.disabled || false}
              type="checkbox"
            />
          </label>
          <label className="toggleControl">
            <span>Raw proxy</span>
            <input
              ref={rawProxyRef}
              defaultChecked={props.toHandle?.data_input.raw_proxy || false}
              type="checkbox"
            />
          </label>
          <label className="toggleControl">
            <span>User agent hack</span>
            <input
              ref={userAgentRef}
              defaultChecked={
                props.toHandle?.data_input.user_agent_hack || false
              }
              type="checkbox"
            />
          </label>
        </div>

        <form
          className="monitorForm"
          onSubmit={(e) =>
            Promise.resolve(e.preventDefault())
              .then(() => update(null))
              .then(() => {
                if (disabledRef.current!.checked)
                  throw new Error("Job is disabled");
                return getData();
              })
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
                resp_data.err
                  ? Promise.reject(resp_data.err)
                  : update(resp_data)
              )
              .catch((err) => {
                update({ err: `${err}` } as any);
                throw err;
              })
          }
        >
          <div className="fieldGrid">
            <label className="field fieldFull">
              <span className="fieldLabel">URL</span>
              <input
                ref={urlRef}
                defaultValue={props.toHandle?.data_input.url}
                type="text"
              />
            </label>
            <label className="field">
              <span className="fieldLabel">Params</span>
              <input
                ref={paramsRef}
                defaultValue={
                  defaultParamsValue === null
                    ? undefined
                    : JSON.stringify(defaultParamsValue)
                }
                type="text"
              />
            </label>
            <label className="field">
              <span className="fieldLabel">Cookies</span>
              <input
                ref={cookiesRef}
                defaultValue={
                  defaultCookiesValue === null
                    ? undefined
                    : JSON.stringify(defaultCookiesValue)
                }
                type="text"
              />
            </label>
            <label className="field fieldFull">
              <span className="fieldLabel">CSS selector</span>
              <input
                ref={cssSelectorRef}
                disabled={props.toHandle?.data_input.send_evaluation || false}
                defaultValue={props.toHandle?.data_input.selector || undefined}
                type="text"
              />
            </label>
            <div className="codeField fieldFull">
              <span className="fieldLabel">JS evaluate</span>
              <label className="toggleControl">
                <span>Transform evaluation to img</span>
                <input
                  onChange={() =>
                    (cssSelectorRef.current!.disabled =
                      evaluationToImgRef.current!.checked)
                  }
                  defaultChecked={
                    props.toHandle?.data_input.send_evaluation || false
                  }
                  ref={evaluationToImgRef}
                  type="checkbox"
                />
              </label>
              <textarea
                defaultValue={props.toHandle?.data_input.evaluate || undefined}
                ref={evaluateRef}
              />
            </div>
          </div>
          <div className="formActions">
            <input type="submit" value="Check Screenshot" />
          </div>
        </form>

        <div className="previewPanel">
          {resp_data === undefined ? undefined : resp_data === null ? (
            <img src={loading} alt="" />
          ) : resp_data.err ? (
            <pre className="errorOutput">{resp_data.err}</pre>
          ) : (
            <div>
              <img
                src={`data:image/png;base64,${resp_data.img_data}`}
                alt="img_data"
              />
              <pre className="serverOutput">
                {JSON.stringify(
                  { ...resp_data, img_data: undefined },
                  null,
                  2
                )}
              </pre>
            </div>
          )}
        </div>
      </div>
    </section>
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
    send_evaluation: evaluationToImgRef.current!.checked || null,
    user_agent_hack: userAgentRef.current!.checked || null,
    raw_proxy: rawProxyRef.current!.checked || null,
  };
}

function getDisabled(): boolean | null {
  return disabledRef.current!.checked || null;
}

export default ToHandle;
