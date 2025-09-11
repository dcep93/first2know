import firebase from "./firebase/firebase";

import { FcGoogle } from "react-icons/fc";
import { sfetch, url } from "./Server";

export const USER_STORAGE_KEY = "user.v1";

function User(props: {
  user: string | null;
  update: (user: string | null) => void;
}) {
  return props.user ? (
    <div>
      <div>
        {props.user}
        <button
          onClick={() => {
            localStorage.removeItem("login");
            props.update(null);
          }}
          className="button"
        >
          Log out
        </button>
        {isAdmin(props.user) ? (
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
              sfetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: result.user.getIdToken() }),
              }).then((resp) => resp.json())
            )
            .then((resp: { email: string; key: string }) => {
              if (!resp.email) {
                throw new Error("no email");
              }
              return resp;
            })
            .then((resp) =>
              localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(resp))
            )
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

export function isAdmin(user: string): boolean {
  return ["dcep93@gmail.com"].includes(user);
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
