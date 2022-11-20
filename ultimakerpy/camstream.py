from argparse import ArgumentParser
import cv2


def http_streaming(url: str, name: str) -> None:
    cap = cv2.VideoCapture(url)

    try:
        while(True):
            frame = cap.read()[1]
            cv2.imshow(name, frame)
    finally:
        cap.release()
        cv2.destroyAllWindows()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('-n', '--name', help='window name', default='frame')
    parser.add_argument('-u', '--url', help='streaming url', default=None)
    args = parser.parse_args()

    if args.url is not None:
        http_streaming(args.url, args.name)


if __name__ == '__main__':
    main()
