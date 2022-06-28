import React from "react";
import firebase, { AllToHandleType } from "./firebase";
import loading from "./loading.gif";

type PropsType = {
  allToHandle: AllToHandleType;
  img_data: string | undefined;
} & StateProps;

export type StateProps = {
  k: string | undefined;
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
    const toHandle = this.props.allToHandle[this.props.k!];
    const data_output = toHandle?.data_output;
    if (data_output) {
      if (data_output.error) {
        this.setState({ img_data: undefined });
        this.props.reject!(data_output.error!.message);
        return;
      }
      if (data_output.img_data) {
        console.log(data_output.times);
        firebase
          .deleteToHandle(this.props.k!)
          .then(() => this.props.resolve!())
          .then(() => this.setState({ img_data: data_output.img_data }));
      } else if (this.state.img_data !== null) {
        this.setState({ img_data: null });
      }
    }
  }

  render() {
    return <ImgRenderer img_data={this.state.img_data} />;
  }
}

function ImgRenderer(props: { img_data: string | undefined | null }) {
  return (
    <img
      src={
        props.img_data === undefined
          ? undefined
          : props.img_data === null
          ? loading
          : `data:image/png;base64,${props.img_data}`
      }
      alt=""
    ></img>
  );
}

export default ScreenshotFetcher;
