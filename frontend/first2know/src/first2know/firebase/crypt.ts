import { Fernet } from "fernet-nodejs";

function encrypt(unencrypted_string: string, fernet_key_str: string): string {
  return Fernet.encrypt(unencrypted_string, fernet_key_str);
}

function decrypt(encrypted_string: string, fernet_key_str: string): string {
  return Fernet.decrypt(encrypted_string, fernet_key_str);
}

const vars = { encrypt, decrypt };
export default vars;
