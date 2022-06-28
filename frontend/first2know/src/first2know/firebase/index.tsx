import React from "react";
import firebase from "./firebase";

export type AllToHandleType = {
  [key: string]: ToHandleType;
};

export type DataType = {
  img_data: string;
  times: number[];
  evaluation?: any;
  error?: { version: string; time: number; message: string };
};

export type ToHandleType = {
  data_input: ScreenshotType;
  data_output: DataType;
  user_name: string;
  encrypted: string;
};

export type ScreenshotType = {
  url: string;
  params: { [s: string]: any } | null;
  selector: string | null;
  evaluate: string | null;
  evaluation_to_img: boolean;
};

function pushToHandle(toHandle: ToHandleType): Promise<string> {
  return firebase._push(`/to_handle/`, toHandle);
}

function deleteToHandle(key: string): Promise<void> {
  return firebase._delete(`/to_handle/${key}`);
}

function updateToHandle(key: string, toHandle: ToHandleType): Promise<void> {
  return firebase._set(`/to_handle/${key}`, toHandle);
}

export class FirebaseWrapper<T> extends React.Component<{}, { state: T }> {
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
        )({ state })
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
