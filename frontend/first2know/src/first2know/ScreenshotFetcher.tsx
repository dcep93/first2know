import { useState } from "react";
import { AllToHandleType } from "./firebase";
import ImgRenderer from "./ImgRenderer";
import Listener from "./Listener";

function ScreenshotFetcher(props: {
  img_data: string | null | undefined;
  allToHandle: AllToHandleType;
  listenerF: (
    updateImgData: (img_data: string | null | undefined) => void
  ) => void;
}) {
  const [img_data, updateImgData] = useState(props.img_data);
  return (
    <>
      <ImgRenderer img_data={img_data} />
      <Listener
        f={() =>
          props.listenerF(
            (new_img_data) =>
              new_img_data !== img_data && updateImgData(new_img_data)
          )
        }
        p={props.allToHandle}
      />
    </>
  );
}

export default ScreenshotFetcher;
