import { initializeApp } from "firebase/app"; // no compat for new SDK
import {
  Database,
  get,
  getDatabase,
  onValue,
  push,
  ref,
  remove,
  set,
} from "firebase/database";

const project = "first2know";

const config = {
  databaseURL: `https://${project}-default-rtdb.firebaseio.com/`,
};

var database: Database;
type ResultType = { val: () => BlobType | null };
type BlobType = any;

declare global {
  interface Window {
    firebaseinitialized: boolean;
  }
}
window.firebaseinitialized = false;
if (!window.firebaseinitialized) {
  window.firebaseinitialized = true;
  var app = initializeApp(config);
  database = getDatabase(app);
}

function _connect(path: string, callback: (value: BlobType) => void): void {
  onValue(ref(database, `${path}`), (snapshot: ResultType) => {
    var val = snapshot.val();
    console.log("firebase", Date.now() / 1000, window.location.href, val);
    callback(val);
  });
}

function _get(path: string): BlobType {
  return get(ref(database, `${path}`));
}

function _set(path: string, obj: BlobType): Promise<void> {
  return set(ref(database, `${path}`), obj);
}

function _push(path: string, obj: BlobType): Promise<string> {
  return push(ref(database, `${path}`), obj).then((pushed) => pushed.key!);
}

function _delete(path: string): Promise<void> {
  return remove(ref(database, `${path}`));
}

const ex = {
  _connect,
  _get,
  _set,
  _push,
  _delete,
};

export default ex;
