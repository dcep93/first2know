import { Secret, Token } from "fernet";

function encrypt(unencrypted_string: string, secret: Secret): string {
  const token = new Token({ secret, time: Date.now() });
  return token.encode(unencrypted_string);
}

function decrypt(encrypted_string: string, secret: Secret): string {
  const token = new Token({ secret, token: encrypted_string, ttl: 0 });
  return token.decode();
}

function getSecret(fernet_key_str: string): Secret {
  return new Secret(fernet_key_str);
}

const vars = { encrypt, decrypt, getSecret };
export default vars;
