import qrfontain
import tempfile
import os
import PIL
import hashlib


def generate_random_file(size) -> str:
    """
    Generate a random files with {size} bytes
    """

    tmp_dir = tempfile.gettempdir()
    filename = f"{tmp_dir}/test_data.bytes"
    with open(filename, "wb") as file:
        file.write(os.urandom(size))

    return filename


def hash_file(filename: str) -> str:
    """
    Compute hash of a file
    """
    hash = hashlib.new("md5")
    with open(filename, "rb") as f:
        while block := f.read(4096):
            hash.update(block)

    return hash.hexdigest()


def test_encode_and_decode_data():

    size = 5_000

    source_file = generate_random_file(size)
    target_file = os.path.join(tempfile.gettempdir(), "qrfontain_target.data")

    print("Encoding ... ")
    images = []
    with open(source_file, "rb") as source, open(target_file, "wb") as dest:

        # Encode
        images = qrfontain.data_to_qrcode(source)
        # Decode
        data = qrfontain.data_from_qrcode(images)
        dest.write(data)

    assert os.path.getsize(source_file) == os.path.getsize(target_file)
    assert hash_file(source_file) == hash_file(target_file)


def test_encode_and_decode_file():

    size = 5_000
    source_file = generate_random_file(size)
    target_file = os.path.join(tempfile.gettempdir(), "qrfontain_target.data")

    # Encode
    images = qrfontain.file_to_qrcode(source_file)
    # Decode
    qrfontain.file_from_qrcode(target_file, images)

    assert os.path.getsize(source_file) == os.path.getsize(target_file)
    assert hash_file(source_file) == hash_file(target_file)


def test_create_frame():

    size = 5_000
    frame_count = 10
    source_file = generate_random_file(size)

    with tempfile.TemporaryDirectory() as dest_dir:
        qrfontain.create_frames(source_file, dest_dir, frame_count=frame_count)

        files = [f for f in os.listdir(dest_dir) if f.endswith("png")]
        assert len(files) == frame_count


def test_create_video():
    size = 5_000
    frame_count = 10
    source_file = generate_random_file(size)
    video_file = os.path.join(tempfile.gettempdir(), "qrfontain.webm")

    qrfontain.create_video(source_file, video_file)

    print(source_file)
    assert os.path.exists(source_file)


# def test_encode_video():
#     size = 1_000_000
#     filename = generate_random_file(size)

#     qrfontain.create_video(filename, "/tmp/test.webm")
