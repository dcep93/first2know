import { UserType } from "./firebase";

import firebase from "./firebase/firebase";

import { FcGoogle } from "react-icons/fc";
import { url } from "./Server";

function User(props: {
  user: UserType | null;
  update: (user: UserType | null) => void;
}) {
  return props.user ? (
    <div>
      <div>
        {props.user.email}
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
            .then((result) => ({
              email: result.user.email!,
            }))
            .then((user) => {
              if (!user.email) {
                throw new Error("no email");
              }
              return user;
            })
            .then((user: UserType) =>
              localStorage.setItem("login", JSON.stringify(user))
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

export function isAdmin(user: UserType): boolean {
  return ["dcep93@gmail.com"].includes(user.email);
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
