import React from "react";
import firebase, { AllToHandleType, ScreenshotType } from "./firebase";
import loading from "./loading.gif";

class ScreenshotFetcher extends React.Component<
  {
    key?: string;
    allToHandle: AllToHandleType;
    resolve?: (s: ScreenshotType) => void;
    reject?: (s: string) => void;
  },
  { img_data: string | undefined | null }
> {
  componentDidUpdate() {
    const toHandle = this.props.allToHandle[this.props.key!];
    const data_output = toHandle?.data_output;
    if (data_output) {
      if (data_output.error) {
        this.setState({ img_data: undefined });
        this.props.reject!(data_output.error!.message);
        return;
      }
      this.setState({ img_data: data_output.img_data });
      firebase
        .deleteToHandle(this.props.key!)
        .then(() => this.props.resolve!(toHandle!.data_input));
    } else if (toHandle) {
      this.setState({ img_data: null });
    }
  }

  render() {
    const img_data = this.state?.img_data;
    return (
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
    );
  }
}

export default ScreenshotFetcher;
