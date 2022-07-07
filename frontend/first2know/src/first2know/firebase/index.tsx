// https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import React from "react";
import firebase from "./firebase";

export type AllToHandleType = {
  [key: string]: ToHandleType;
};

export type ScreenshotDataType = {
  img_url: string;
  md5: string;
  evaluation: any;
};

export type DataOutputType = {
  times: number[];
  screenshot_data?: ScreenshotDataType;
  evaluation?: any;
  error?: { version: string; time: number; message: string };
};

export type UserType = {
  screen_name: string;
  user_id: number;
  encrypted: string;
};

export type DataInputType = {
  url: string;
  params: { [s: string]: any };
  selector: string | null;
  evaluate: string | null;
  evaluation_to_img: boolean;
};

export type ToHandleType = {
  data_input: DataInputType;
  data_output: DataOutputType;
  user: UserType;
  encrypted: string;
};

function pushToHandle(
  data_input: DataInputType,
  encrypted: string,
  user: UserType
): Promise<string> {
  const toHandle: ToHandleType = {
    data_input,
    data_output: { times: [Date.now() / 1000] },
    encrypted,
    user,
  };
  return firebase._push(`/to_handle/`, toHandle);
}

function deleteToHandle(key: string): Promise<void> {
  return firebase._delete(`/to_handle/${key}`);
}

function updateToHandle(key: string, toHandle: {}): Promise<void> {
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
