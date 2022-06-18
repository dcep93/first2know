import React from "react";
import firebase from "./firebase";

export type AllToHandleType = {
  [key: string]: ToHandleType;
};

export type ToHandleType = {
  key: string;
  img_data: string;
  url: string;
  user: string;
  e_fetch_params?: string;
  css_selector?: string;
};

function setToHandle(toHandle: ToHandleType) {
  const key = toHandle.key;
  firebase._set(`/to_handle/${key}`, toHandle);
}

function deleteToHandle(key: string) {
  firebase._delete(`/to_handle/${key}`);
}

export class FirebaseWrapper<T> extends React.Component<{}, T> {
  static firebaseWrapperComponent: FirebaseWrapper<any>;
  componentDidMount() {
    const oldComponent = FirebaseWrapper.firebaseWrapperComponent;
    FirebaseWrapper.firebaseWrapperComponent = this;
    if (oldComponent) {
      this.setState(oldComponent.state);
    } else {
      const title = this.getTitle();
      if (title !== null) document.title = title;
      firebase._connect(this.getFirebasePath(), (state) =>
        FirebaseWrapper.firebaseWrapperComponent.setState.bind(
          FirebaseWrapper.firebaseWrapperComponent
        )(state)
      );
    }
  }

  getTitle(): string | null {
    return null;
  }

  getFirebasePath(): string {
    return `/`;
  }

  render() {
    return <pre>{JSON.stringify(this.state, null, 2)}</pre>;
  }
}

const ex = {
  setToHandle,
  deleteToHandle,
};

export default ex;
