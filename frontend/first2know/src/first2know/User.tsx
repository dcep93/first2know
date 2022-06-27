import TwitterLogin from "./TwitterLogin";

import React from "react";
import { url } from "./Server";

export type UserType = {
  screen_name: string;
  user_id: string;
  encrypted: string;
} | null;

type PropsType = { user: UserType; update: (user: UserType) => void };

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
        <p>Authenticated</p>
        <div>{this.props.user.screen_name}</div>
        <div>
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

export default User;
