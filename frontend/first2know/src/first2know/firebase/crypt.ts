// @ts-ignore
const Fernet = window.fernet;

const { Secret, Token } = Fernet;

function encrypt(unencrypted_string: string, secret: typeof Secret): string {
  const token = new Token({ secret, time: Date.now() });
  return token.encode(unencrypted_string);
}

function decrypt(encrypted_string: string, secret: typeof Secret): string {
  const token = new Token({ secret, token: encrypted_string, ttl: 0 });
  return token.decode();
}

function getSecret(fernet_key_str: string): typeof Secret {
  return new Secret(fernet_key_str);
}

const vars = { encrypt, decrypt, getSecret };
export default vars;
