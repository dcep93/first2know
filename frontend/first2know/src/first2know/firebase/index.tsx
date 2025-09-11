// https://console.firebase.google.com/u/0/project/first2know/database/first2know-default-rtdb/data

import React from "react";
import { LOCAL_USER } from "../User";
import crypt from "./crypt";
import firebase from "./firebase";

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
  params: { [s: string]: any } | null;
  cookies: { [domain: string]: string } | null;
  selector: string | null;
  evaluate: string | null;
  evaluation_to_img: boolean | null;
  raw_proxy: boolean | null;
  user_agent_hack: boolean | null;
};

export type ToHandleType = {
  key: string;
  data_input: DataInputType;
  data_output: DataOutputType | null;
  user: string;
};

type WrappedToHandleType = { user: string; encrypted: string };

function filterDict(d: Record<string, any>): Record<string, any> {
  return Object.fromEntries(
    Object.entries(d)
      .map(([k, v]) => ({ k, v }))
      .filter(({ v }) => v)
      .map(({ k, v }) => [k, v])
  );
}

function encryptToHandle(toHandle: ToHandleType): WrappedToHandleType {
  const encrypted = crypt.encrypt(
    JSON.stringify({
      ...filterDict({
        ...toHandle,
        data_input: filterDict(toHandle.data_input),
      }),
    }),
    LOCAL_USER!.fernet_secret
  );
  return { user: LOCAL_USER!.email, encrypted };
}

function pushToHandle(data_input: DataInputType): Promise<string> {
  const toHandle: ToHandleType = {
    data_input,
    data_output: null,
    user: LOCAL_USER!.email,
    key: "",
  };
  return firebase._push(`/to_handle/`, encryptToHandle(toHandle));
}

function deleteToHandle(key: string): Promise<void> {
  return firebase._delete(`/to_handle/${key}`);
}

function updateToHandle(toHandle: ToHandleType): Promise<void> {
  return firebase._set(`/to_handle/${toHandle.key}`, encryptToHandle(toHandle));
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
      firebase._connect(
        this.getFirebasePath(),
        (rawToHandle: Record<string, WrappedToHandleType>) =>
          Promise.resolve()
            .then(() =>
              Object.entries(rawToHandle || {})
                .map(([key, obj]) => ({ key, obj }))
                .filter(({ obj }) => obj.user === LOCAL_USER?.email)
                .map(({ key, obj }) => {
                  try {
                    return {
                      ...JSON.parse(
                        crypt.decrypt(obj.encrypted, LOCAL_USER!.fernet_secret)
                      ),
                      key,
                      ...obj,
                    };
                  } catch (err) {
                    return null;
                  }
                })
                .filter(Boolean)
            )
            .then((state: ToHandleType[]) =>
              FirebaseWrapper.firebaseWrapperComponent.setState.bind(
                FirebaseWrapper.firebaseWrapperComponent
              )({ state })
            )
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
