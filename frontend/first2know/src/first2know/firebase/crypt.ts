// @ts-ignore
const Fernet = window.fernet;

Fernet.ttl = 0;

const { Secret, Token } = Fernet;

function encrypt(unencrypted_string: string, secret: typeof Secret): string {
  const token = new Token({ secret });
  return token.encode(unencrypted_string);
}

function decrypt(
  encrypted_string: string,
  secret: typeof Secret
): string | null {
  const token = new Token({ secret, token: encrypted_string });
  return token.decode();
}

const s = getSecret("12341234123412341234123412341234");
console.log(s);
const e = encrypt("helloworld", s);
const now = Date.now();
console.log(new Date());
const int = setInterval(() => {
  const d = decrypt(e, s);
  if (!d) {
    console.log(Date.now() - now);
    clearInterval(int);
  }
}, 100);

function getSecret(fernet_key_str: string): typeof Secret {
  return new Secret(fernet_key_str);
}

const vars = { encrypt, decrypt, getSecret };
export default vars;
