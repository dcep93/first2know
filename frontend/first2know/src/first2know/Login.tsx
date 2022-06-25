import TwitterLogin from "./TwitterLogin";

import React from "react";
import { url } from "./Server";

type UserType = { screen_name: string; user_id: string };

class Login extends React.Component<{}, { user: UserType | null }> {
  constructor(props: {}) {
    super(props);

    this.state = { user: null };
  }

  render() {
    return this.state.user ? (
      <div>
        <p>Authenticated</p>
        <div>{this.state.user.screen_name}</div>
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
        forceLogin={true}
      />
    );
  }

  login(user: UserType) {
    this.setState({ user });
  }

  logout() {
    this.setState({ user: null });
  }

  onSuccess(response: any) {
    response.json().then((user: UserType) => this.login(user));
  }

  onFailed(error: string) {
    alert(error);
  }
}

export default Login;
