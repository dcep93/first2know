import React, { createRef } from "react";
import { useNavigate } from "react-router-dom";
import { encrypt } from "./Edit";
import firebase, {
  AllToHandleType,
  ScreenshotType,
  ToHandleType,
} from "./firebase";
import ScreenshotFetcher from "./ScreenshotFetcher";
import { UserType } from "./User";

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
  user: UserType;
  toHandle?: ToHandleType;
  submit?: SubmitType;
  allToHandle: AllToHandleType;
};

class ToHandle extends React.Component<PropsType> {
  render() {
    const navigate = useNavigate();
    const defaultParamsValue = this.props.toHandle?.data_input.params;
    return (
      <div>
        <form onSubmit={(e) => [e.preventDefault(), this.checkScreenShot()]}>
          <div>
            url:{" "}
            <input
              ref={urlRef}
              defaultValue={this.props.toHandle?.data_input.url}
              type="text"
            />
          </div>
          <div title={"will be encrypted"}>
            cookie: <input ref={cookieRef} type="text" />
          </div>
          {this.props.toHandle && (
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
              defaultValue={
                this.props.toHandle?.data_input.selector || undefined
              }
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
              defaultChecked={this.props.toHandle?.data_input.evaluation_to_img}
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
        <ScreenshotFetcher />
        {this.props.submit && (
          <button onClick={() => this.onSubmit(navigate)}>Submit</button>
        )}
      </div>
    );
  }

  onSubmit(navigate: (key: string) => void) {
    const old_encrypted = getOldEncrypted(this.props.toHandle);
    Promise.resolve()
      .then(() => this.getData(old_encrypted))
      .then((data_input) =>
        this.props.submit!({ old_encrypted, ...data_input })
      )
      .then((key) => navigate(key))
      .catch((err) => {
        alert(err);
        throw err;
      });
  }

  getData(old_encrypted: string | null): Promise<ScreenshotType> {
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
    return this.validateScreenshot(data_input, old_encrypted);
  }

  validateScreenshot(
    data_input: ScreenshotType,
    old_encrypted: string | null
  ): Promise<ScreenshotType> {
    return encrypt(data_input, this.props.user, old_encrypted)
      .then((encrypted) =>
        firebase.pushToHandle(
          data_input,
          encrypted,
          this.props.user.screen_name
        )
      )
      .then(() => p)
      .catch((err) => {
        alert(err);
        throw err;
      })
      .then((di) => di);
  }

  checkScreenShot() {
    const old_encrypted = getOldEncrypted(this.props.toHandle);
    return this.getData(old_encrypted);
  }
}

function getOldEncrypted(toHandle: ToHandleType | undefined) {
  return toHandle === undefined
    ? null
    : reuseCookieRef.current?.checked
    ? toHandle.encrypted
    : null;
}

export default ToHandle;
