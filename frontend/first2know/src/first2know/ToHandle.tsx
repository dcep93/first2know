import React, { createRef } from "react";
import { useNavigate } from "react-router-dom";
import { encrypt } from "./Edit";
import firebase, {
  AllToHandleType,
  DataInputType,
  ToHandleType,
  UserType,
} from "./firebase";
import ScreenshotFetcher from "./ScreenshotFetcher";

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

type PropsType = {
  user: UserType;
  toHandle?: ToHandleType;
  submit: SubmitType;
  allToHandle: AllToHandleType;
};

class ToHandle extends React.Component<
  PropsType,
  {
    k?: string;
    resolve?: () => void;
    reject?: (s: string) => void;
  }
> {
  render() {
    const defaultParamsValue = this.props.toHandle?.data_input.params;
    return (
      <div>
        <form
          onSubmit={(e) =>
            Promise.resolve(e.preventDefault())
              .then(() => this.getData())
              .catch((err) => {
                alert(err);
                throw err;
              })
          }
        >
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
              <textarea
                defaultValue={
                  this.props.toHandle?.data_input.evaluate || undefined
                }
                ref={evaluateRef}
              />
            </div>
          </div>
          <input type="submit" value="Check Screenshot" />
        </form>
        <ScreenshotFetcher
          allToHandle={this.props.allToHandle}
          img_data={this.props.toHandle?.data_output.img_data}
          listenerF={this.listenerF.bind(this)}
        />
        <SubmitableButton
          onSubmit={(navigate) => this.onSubmit(this.props.submit, navigate)}
        />
      </div>
    );
  }

  onSubmit(submit: SubmitType, navigate: (key: string) => void) {
    Promise.resolve()
      .then(() => this.getData())
      .then((data_input) => submit(data_input))
      .then((key) => navigate(key))
      .catch((err) => {
        alert(err);
        throw err;
      });
  }

  getData(): Promise<DataInputType & { old_encrypted: string | null }> {
    const old_encrypted =
      this.props.toHandle === undefined
        ? null
        : reuseCookieRef.current?.checked
        ? this.props.toHandle.encrypted
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
      evaluation_to_img: evaluationToImgRef.current!.checked,
    };
    if (data_input.url === "") {
      throw Error("need to have a url");
    }
    // always fetch screenshot
    // to validate the payload
    const p = new Promise<void>((resolve, reject) => {
      this.setState({ resolve, reject });
    });
    return encrypt(data_input, this.props.user, old_encrypted)
      .then((encrypted) =>
        firebase.pushToHandle(
          data_input,
          encrypted,
          this.props.user.screen_name
        )
      )
      .then((k) => this.setState({ k }))
      .then(() => p)
      .catch((err) => {
        this.setState({
          resolve: undefined,
          reject: undefined,
          k: undefined,
        });
        throw err;
      })
      .then(() => {
        this.setState({
          resolve: undefined,
          reject: undefined,
          k: undefined,
        });
        return data_input;
      })
      .then(({ no_tweet, ...data_input }) => ({
        old_encrypted,
        ...data_input,
      }));
  }

  listenerF(): Promise<string | null | undefined> | null {
    const data_output = this.props.allToHandle[this.state.k!]?.data_output;
    if (data_output) {
      if (data_output.error) {
        return firebase
          .deleteToHandle(this.state.k!)
          .then(() => this.state.reject!(data_output.error!.message))
          .then(() => undefined);
      } else if (data_output.img_data) {
        return firebase
          .deleteToHandle(this.state.k!)
          .then(() => this.state.resolve!())
          .then(() => data_output.img_data);
      } else {
        return Promise.resolve(null);
      }
    }
    return null;
  }
}

function SubmitableButton(props: {
  onSubmit: (navigate: (key: string) => void) => void;
}) {
  const navigate = useNavigate();
  return <button onClick={() => props.onSubmit(navigate)}>Submit</button>;
}

export default ToHandle;
