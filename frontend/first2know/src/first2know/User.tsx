import firebase from "./firebase/firebase";

import { Secret } from "fernet";
import { FcGoogle } from "react-icons/fc";
import { sfetch, url } from "./Server";
import crypt from "./firebase/crypt";

export const USER_STORAGE_KEY = "user.v1";
type LocalUserType = {
  email: string;
  fernet_key_str: string;
  fernet_secret: Secret;
};
export const LOCAL_USER: LocalUserType | null = JSON.parse(
  localStorage.getItem(USER_STORAGE_KEY)!
);
if (LOCAL_USER)
  LOCAL_USER.fernet_secret = crypt.getSecret(LOCAL_USER.fernet_key_str);

function User() {
  return LOCAL_USER ? (
    <div>
      <div>
        {LOCAL_USER.email}
        <button
          onClick={() => {
            localStorage.removeItem(USER_STORAGE_KEY);
            window.location.reload();
          }}
          className="button"
        >
          Log out
        </button>
        {isAdmin(LOCAL_USER.email) ? (
          <span>
            {" "}
            <a href={url}>admin</a>
          </span>
        ) : null}
      </div>
    </div>
  ) : (
    <div>
      <button
        style={{ display: "flex", alignItems: "center" }}
        onClick={() =>
          Promise.resolve()
            .then(() =>
              firebase.signInWithPopup(firebase.auth, firebase.provider)
            )
            .then((result) =>
              result.user.getIdToken().then((token) =>
                sfetch(`${url}/login`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ token }),
                })
                  .then((resp) => resp.json())
                  .then((resp: LocalUserType) => {
                    if (resp.email !== result.user.email) {
                      throw new Error("email");
                    }
                    return resp;
                  })
              )
            )
            .then((resp) => {
              localStorage.clear();
              localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(resp));
            })
            .then(() => window.location.reload())
            .catch((err) => alert(err))
        }
      >
        <span>LOGIN</span>
        <FcGoogle style={{ fontSize: "large" }} />
      </button>
    </div>
  );
}

export function isAdmin(email: string): boolean {
  return ["dcep93@gmail.com"].includes(email);
}

export function hashCode(s: string): number {
  var hash = 0;
  for (var i = 0; i < s.length; i++) {
    var code = s.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

export default User;
