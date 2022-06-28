import React from "react";
import firebase, { AllToHandleType } from "./firebase";
import loading from "./loading.gif";

type PropsType = {
  allToHandle: AllToHandleType;
  img_data: string | undefined;
} & StateProps;

export type StateProps = {
  key?: string;
  resolve?: () => void;
  reject?: (s: string) => void;
};

class ScreenshotFetcher extends React.Component<
  PropsType,
  { img_data: string | undefined | null }
> {
  constructor(props: PropsType) {
    super(props);
    this.state = { img_data: this.props.img_data };
  }

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
        .then(() => this.props.resolve!());
    } else if (toHandle) {
      this.setState({ img_data: null });
    }
  }

  render() {
    const img_data = this.state.img_data;
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
