import TwitterLogin from "./TwitterLogin";

import { UserType } from "./firebase";
import { url } from "./Server";

function User(props: {
  user: UserType | null;
  update: (user: UserType | null) => void;
}) {
  return props.user ? (
    <div>
      <div>
        {props.user.screen_name}
        <button
          disabled={window.location.hostname === "localhost"}
          onClick={() => {
            localStorage.removeItem("login");
            props.update(null);
          }}
          className="button"
        >
          Log out
        </button>
        {isAdmin(props.user) ? <span> admin</span> : null}
      </div>
    </div>
  ) : (
    <TwitterLogin
      // @ts-ignore
      loginUrl={`${url}/twitter/access_token`}
      onFailure={(error: string) => alert(error)}
      onSuccess={(response: any) =>
        response.json().then((user: UserType) => {
          localStorage.setItem("login", JSON.stringify(user));
          props.update(user);
        })
      }
      requestTokenUrl={`${url}/twitter/request_token`}
    />
  );
}

export function isAdmin(user: UserType): boolean {
  return [-416693726].includes(hashCode(user.encrypted || ""));
}

function hashCode(s: string): number {
  var hash = 0;
  for (var i = 0; i < s.length; i++) {
    var code = s.charCodeAt(i);
    hash = (hash << 5) - hash + code;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

export default User;
