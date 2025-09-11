// @ts-ignore
const Fernet = window.fernet;

const { Secret, Token } = Fernet;

function encrypt(unencrypted_string: string, secret: typeof Secret): string {
  const token = new Token({ secret });
  return token.encode(unencrypted_string);
}

function decrypt(
  encrypted_string: string,
  secret: typeof Secret
): string | null {
  try {
    const token = new Token({ secret, token: encrypted_string });
    return token.decode();
  } catch (err) {
    return null;
  }
}

function getSecret(fernet_key_str: string): typeof Secret {
  return new Secret(fernet_key_str);
}

const vars = { encrypt, decrypt, getSecret };
export default vars;
