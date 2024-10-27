import argparse
import qrfontain


def main_cli():
    parser = argparse.ArgumentParser(description="Create a video from a sample of fontain qr code")

    parser.add_argument("--input", "-i", required=True, help="Any input filename ")
    parser.add_argument("--output", "-o", required=True, help="webm video file output")
    parser.add_argument("--frame_count", "-c", default=30, help="How many frame to export")
    parser.add_argument("--fps", "-f", default=30, help="Frame per second")

    args = parser.parse_args()

    qrfontain.create_video(args.input, args.output, fps=args.fps, frame_count=args.frame_count)


if __name__ == "__main__":
    main_cli()
