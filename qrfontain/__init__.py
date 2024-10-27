import base64
import os
import io
import qrcode
import tempfile
import shutil
import zbarlight
import lt
import tempfile
from tqdm import tqdm
from PIL import Image
from typing import Generator
from moviepy.editor import ImageSequenceClip


DEFAULT_CHUNK_SIZE = 2200
DEFAULT_QR_VERISON = 40
DEFAULT_QR_SIZE = 3
DEFAULT_QR_CORRECTION = qrcode.ERROR_CORRECT_L


def data_to_qrcode(
    data: io.BytesIO(),
    chunk_size=DEFAULT_CHUNK_SIZE,
    qrcode_version=DEFAULT_QR_VERISON,
    qrcode_size=DEFAULT_QR_SIZE,
    qrcode_correction=DEFAULT_QR_CORRECTION,
) -> Generator[Image, None, None]:
    """
    Splits a binary file into fixed-size chunks and generates qrcode using LT fontain code.
    """

    for block in lt.encode.encoder(data, chunk_size):
        qr = qrcode.QRCode(
            version=qrcode_version, box_size=qrcode_size, error_correction=qrcode_correction
        )

        encoded_data = base64.b64encode(block).decode("utf-8")
        qr.add_data(encoded_data)
        yield qr.make_image()


def data_from_qrcode(images: Generator[Image, None, None]) -> io.BytesIO:

    decoder = lt.decode.LtDecoder()
    for image in images:
        data = decode_qrcode(image)
        if data:
            payload = io.BytesIO(data)
            header = lt.decode._read_header(payload)
            block = lt.decode._read_block(header[1], payload)
            decoder.consume_block((header, block))

            if decoder.is_done():
                break

    return decoder.bytes_dump()


def decode_qrcode(image: Image) -> bytes:
    data = zbarlight.scan_codes(["qrcode"], image)
    if data:
        data = data[0].decode()
        data = base64.b64decode(data)
        return data

    return None


def file_to_qrcode(filename: str, **kwargs) -> Generator[Image, None, None]:
    """
    Yield QR code from filename
    """
    with open(filename, "rb") as file:
        yield from data_to_qrcode(file)


def file_from_qrcode(filename: str, images: Generator[Image, None, None]):
    """
    Decode images and create a new filename

    """

    with open(filename, "wb") as file:
        file.write(data_from_qrcode(images))


def create_frames(filename: str, output_dir: str, frame_count: int = None, **kwargs):
    """
    Generate {frame_count} qr code from a file
    If frame_count is None, estimate it using chunk size and file size

    """

    chunk_size = kwargs.get("chunk_size", DEFAULT_CHUNK_SIZE)
    file_size = os.path.getsize(filename)

    if frame_count is None:
        # Four time the file size should be enough
        frame_count = int(file_size / chunk_size) * 4

    images = file_to_qrcode(filename, **kwargs)

    for i, image in tqdm(enumerate(images), total=frame_count):

        if i >= frame_count:
            break
        name = f"{i:010}.png"
        image.convert("RGB").save(os.path.join(output_dir, name))


def create_video(
    source_file: str,
    video_file: str,
    fps: int = 30,
    bitrate: str = "30000k",
    frame_count: int = None,
    **kwargs,
):
    """
    Create Qr code frames and make a video with it
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        create_frames(source_file, tmp_dir, kwargs.get("frame_count"))

        images = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) if f.endswith(".png")]
        clip = ImageSequenceClip(images, fps=fps)
        clip.write_videofile(video_file, bitrate=bitrate)
