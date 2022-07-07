import TwitterLogin from "./TwitterLogin";

import React from "react";
import { UserType } from "./firebase";
import { url } from "./Server";

type PropsType = {
  user: UserType | null;
  update: (user: UserType | null) => void;
};

class User extends React.Component<PropsType> {
  render() {
    return this.props.user ? (
      <div>
        <div>
          {this.props.user.screen_name}
          <span> </span>
          <button
            disabled={window.location.hostname === "localhost"}
            onClick={this.logout.bind(this)}
            className="button"
          >
            Log out
          </button>
          {isAdmin(this.props.user) ? <span> admin</span> : null}
        </div>
      </div>
    ) : (
      <TwitterLogin
        // @ts-ignore
        loginUrl={`${url}/twitter/access_token`}
        onFailure={this.onFailed}
        onSuccess={this.onSuccess.bind(this)}
        requestTokenUrl={`${url}/twitter/request_token`}
      />
    );
  }

  login(user: UserType) {
    localStorage.setItem("login", JSON.stringify(user));
    this.props.update(user);
  }

  logout() {
    localStorage.removeItem("login");
    this.props.update(null);
  }

  onSuccess(response: any) {
    response.json().then((user: UserType) => this.login(user));
  }

  onFailed(error: string) {
    alert(error);
  }
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
