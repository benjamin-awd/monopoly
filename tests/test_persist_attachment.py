import os

import pytest

from monopoly.gmail.attachment import Attachment


@pytest.fixture
def attachment():
    return Attachment(name="test.pdf", file_byte_string=b"Test data")


def test_temporary_file_create_and_cleanup(attachment: Attachment):
    """
    Test that file exists during context manager, and is
    cleaned up after the context manager closes
    """
    with attachment.persist_attachment_to_disk(attachment) as file_path:
        assert os.path.exists(file_path)

    assert not os.path.exists(file_path)


def test_persist_attachment_to_disk_writes_correct_data(attachment: Attachment):
    """
    Test that correct data is written to file
    """
    with attachment.persist_attachment_to_disk(attachment) as file_path:
        with open(file_path, "rb") as file:
            file_contents = file.read()
            assert file_contents == attachment.file_byte_string


def test_persist_attachment_to_disk_exception_cleanup(attachment: Attachment):
    """
    Test that file is deleted if an exception occurs
    """
    try:
        with attachment.persist_attachment_to_disk(attachment) as file_path:
            assert os.path.exists(file_path)
            raise Exception("Simulating an error")
    except Exception:
        pass

    assert not os.path.exists(file_path)
