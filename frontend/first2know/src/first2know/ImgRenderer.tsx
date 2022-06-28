import loading from "./loading.gif";

function ImgRenderer(props: { img_data: string | undefined | null }) {
  return (
    <img
      src={
        props.img_data === undefined
          ? undefined
          : props.img_data === null
          ? loading
          : `data:image/png;base64,${props.img_data}`
      }
      alt=""
    ></img>
  );
}

export default ImgRenderer;
