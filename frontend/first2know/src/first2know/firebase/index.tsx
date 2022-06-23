import React from "react";
import firebase from "./firebase";

export type AllToHandleType = {
  [key: string]: ToHandleType;
};

// TODO dcep93 creatorID
export type ToHandleType = {
  data?: string;
  user: string;
  url: string;
  e_cookie?: string;
  params?: { [s: string]: any };
  evaluate?: string;
  selector?: string;
};

function pushToHandle(toHandle: ToHandleType) {
  firebase._push(`/to_handle/`, toHandle);
}

function deleteToHandle(key: string) {
  firebase._delete(`/to_handle/${key}`);
}

function updateToHandle(key: string, toHandle: ToHandleType) {
  firebase._set(`/to_handle/${key}`, toHandle);
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
  pushToHandle,
  deleteToHandle,
  updateToHandle,
};

export default ex;
