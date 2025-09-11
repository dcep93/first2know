// https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import React from "react";
import firebase from "./firebase";

export type AllToHandleType = {
  [key: string]: ToHandleType;
};

export type ScreenshotDataType = {
  md5: string;
  elapsed: number;
  img_data: string;
  evaluation?: string;
};

export type DataOutputType = {
  screenshot_data?: ScreenshotDataType;
  error: { version: string; time: number; message: string } | null;
};

export type DataInputType = {
  url: string;
  params: { [s: string]: any };
  selector: string | null;
  evaluate: string | null;
  evaluation_to_img: boolean | null;
  raw_proxy: boolean | null;
  user_agent_hack: boolean | null;
};

export type ToHandleType = {
  data_input: DataInputType;
  data_output: DataOutputType | null;
  user: string;
};

function _FBToHandle(toHandle: ToHandleType): string {
  return "TODO";
  // const to_md5 = JSON.stringify([toHandle.data_input]);
  // const md5 = to_md5_f(to_md5);
  // console.log({ md5, to_md5 });
  // return {
  //   ...toHandle,
  //   md5,
  //   user: {
  //     ...toHandle.user,
  //   },
  // };
}

function pushToHandle(
  data_input: DataInputType,
  user: string
): Promise<string> {
  const toHandle: ToHandleType = {
    data_input,
    data_output: null,
    user,
  };
  return firebase._push(`/to_handle/`, _FBToHandle(toHandle));
}

function deleteToHandle(key: string): Promise<void> {
  return firebase._delete(`/to_handle/${key}`);
}

function updateToHandle(key: string, toHandle: ToHandleType): Promise<void> {
  return firebase._set(`/to_handle/${key}`, _FBToHandle(toHandle));
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
