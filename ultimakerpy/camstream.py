from argparse import ArgumentParser
from typing import Union
import cv2


WINDOW_SIZE = (640, 480)
FORMAT = 'H264'


def stream(target: Union[str, int], name: str) -> None:
    cap = cv2.VideoCapture(target)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_SIZE[1])
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*list(FORMAT)))
    try:
        while(True):
            frame = cap.read()[1]
            cv2.imshow(name, frame)
            cv2.waitKey(1)
    finally:
        cap.release()
        cv2.destroyAllWindows()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('target', help='streaming target', default=0)
    parser.add_argument('-n', '--name', help='window name', default='frame')
    args = parser.parse_args()
    target, name = args.target, args.name

    if args.target.isdecimal():
        target = int(target)

    stream(target, name)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
