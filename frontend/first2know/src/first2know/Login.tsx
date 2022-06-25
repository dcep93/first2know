import _TwitterLogin from "./TwitterLogin";

import React from "react";
import { url } from "./Server";

type UserType = { screen_name: string; user_id: string };

class TwitterLogin extends _TwitterLogin {
  openPopup() {
    // @ts-ignore
    const w = this.props.dialogWidth;
    // @ts-ignore
    const h = this.props.dialogHeight;
    // const left = screen.width / 2 - w / 2;
    // const top = screen.height / 2 - h / 2;
    const left = 0;
    const top = 0;

    return window.open(
      "",
      "",
      "toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width=" +
        w +
        ", height=" +
        h +
        ", top=" +
        top +
        ", left=" +
        left
    );
  }
}

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
          <button onClick={this.logout} className="button">
            Log out
          </button>
        </div>
      </div>
    ) : (
      <TwitterLogin
        // @ts-ignore
        loginUrl={`${url}/twitter/access_token`}
        onFailure={this.onFailed}
        onSuccess={this.onSuccess}
        requestTokenUrl={`${url}/twitter/request_token`}
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
