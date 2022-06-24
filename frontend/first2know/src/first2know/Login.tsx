import TwitterLogin from "react-twitter-auth";

import React from "react";
import { modalUrl } from "./Server";

type UserType = { email: string; token: string };

class Login extends React.Component<{}, { user: UserType | null }> {
  constructor(props: {}) {
    super(props);

    this.state = { user: null };
  }

  render() {
    return this.state.user ? (
      <div>
        <p>Authenticated</p>
        <div>{this.state.user.email}</div>
        <div>
          <button onClick={this.logout} className="button">
            Log out
          </button>
        </div>
      </div>
    ) : (
      <React.Fragment>
        <TwitterLogin
          loginUrl={`${modalUrl}/twitter/access_token`}
          onFailure={this.onFailed}
          onSuccess={this.onSuccess}
          requestTokenUrl={`${modalUrl}/twitter/request_token`}
        />
      </React.Fragment>
    );
  }

  logout() {
    this.setState({ user: null });
  }

  onSuccess(response: any) {
    const token: string = response.headers.get("x-auth-token");
    response.json().then((user: UserType) => {
      if (token) {
        user.token = token;
        this.setState({ user });
      }
    });
  }

  onFailed(error: string) {
    alert(error);
  }
}

export default Login;
