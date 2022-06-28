import TwitterLogin from "./TwitterLogin";

import React from "react";
import { url } from "./Server";

export type UserType = {
  screen_name: string;
  user_id: string;
  encrypted: string;
};

type PropsType = {
  user: UserType | null;
  update: (user: UserType | null) => void;
};

class User extends React.Component<PropsType> {
  constructor(props: PropsType) {
    super(props);

    const local = localStorage.getItem("login");
    if (local) {
      const user = JSON.parse(local);
      this.props.update(user);
    }
  }

  render() {
    return this.props.user ? (
      <div>
        <div>
          {this.props.user.screen_name}
          <span> </span>
          <button onClick={this.logout.bind(this)} className="button">
            Log out
          </button>
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
  return [-73599652].includes(hashCode(user.encrypted || ""));
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
