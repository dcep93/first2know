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

  componentDidUpdate(prevProps: PropsType) {
    if (this.props.img_data && !prevProps.img_data) {
      this.updateImgData(this.props.img_data);
      return;
    }
    const data_output = this.props.allToHandle[this.props.k!]?.data_output;
    if (data_output) {
      console.log(data_output);
      if (data_output.error) {
        firebase
          .deleteToHandle(this.props.k!)
          .then(() => this.props.reject!(data_output.error!.message))
          .then(() => this.updateImgData(undefined));
      } else if (data_output.img_data) {
        firebase
          .deleteToHandle(this.props.k!)
          .then(() => this.props.resolve!())
          .then(() => this.updateImgData(data_output.img_data));
      } else if (this.state.img_data !== null) {
        this.updateImgData(null);
      }
    }
  }

  updateImgData(img_data: string | undefined | null) {
    if (this.state?.img_data !== img_data) this.setState({ img_data });
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
