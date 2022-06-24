# [first2know.web.app](first2know.web.app)

# [@first2know_t](https://twitter.com/first2know_t)

# deployment

- pushing to github automatically builds and deploys via [workflow.yaml](https://github.com/dcep93/first2know/blob/master/.github/workflows/workflow.yaml)

# database

- currently use firebase realtime database
- security/permissions coming soon!
- maybe convex is on the horizon???

# frontend

- using firebase hosting, which is very convenient

# backend

- use `make -C backend regenauth` and place secrets in modal first2know_s and/or github SECRETS_JSON
- visit [https://dcep93-first2know-app.modal.run/](https://dcep93-first2know-app.modal.run/) to verify working

# secrets

#### required_keys:

- client_id
- client_secret
- api_key
- api_key_secret
- oauth_token
- oauth_token_secret
- redirect_uri
