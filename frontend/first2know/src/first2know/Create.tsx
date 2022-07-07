import { useState } from "react";
import { encrypt } from "./Edit";
import firebase, { AllToHandleType, DataInputType, UserType } from "./firebase";
import Listener, { PromiseC } from "./Listener";

import ToHandle from "./ToHandle";

type ListenerPropsType = {
  k: string | undefined;
  allToHandle: AllToHandleType;
};

function Create(props: {
  user: UserType;
  allToHandle: AllToHandleType;
}): JSX.Element {
  const [p, updateP] = useState<PromiseC>({});
  const [k, updateK] = useState<string | undefined>(undefined);
  return (
    <>
      <Listener
        f={(props: ListenerPropsType) => listenerF(props, p)}
        p={{
          k,
          allToHandle: props.allToHandle,
        }}
      />
      <ToHandle
        user={props.user}
        submit={(data_input) =>
          submitNew(data_input, props.user!, updateP, updateK)
        }
        allToHandle={props.allToHandle}
      />
    </>
  );
}

function submitNew(
  data_input: DataInputType,
  user: UserType,
  updateP: (p: PromiseC) => void,
  updateK: (k: string) => void
): Promise<string> {
  const p = new Promise((resolve, reject) => updateP({ resolve, reject }));
  return encrypt(data_input, user, null)
    .then((encrypted) => firebase.pushToHandle(data_input, encrypted, user))
    .then((k) => {
      updateK(k);
      return p.then(() => k);
    });
}

function listenerF(props: ListenerPropsType, p: PromiseC) {
  const data_output = props.allToHandle[props.k!]?.data_output;
  if (data_output) {
    if (data_output.error) {
      p.reject!(data_output.error!.message);
    } else if (data_output.screenshot_data) {
      p.resolve!();
    }
  }
}

export default Create;
