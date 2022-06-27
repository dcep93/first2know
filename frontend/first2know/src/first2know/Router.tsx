import { useHistory } from "react-router-dom";

export default function goToPath(path: string) {
  useHistory().push(path);
}
