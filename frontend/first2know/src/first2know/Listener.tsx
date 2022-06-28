import React from "react";

class Listener<T> extends React.Component<{ p: T; f: (t: T) => void }> {
  componentDidUpdate() {
    this.props.f(this.props.p);
  }

  render() {
    return null;
  }
}

export type PromiseC = {
  resolve?: (a?: any) => void;
  reject?: (a: any) => void;
};

export default Listener;
