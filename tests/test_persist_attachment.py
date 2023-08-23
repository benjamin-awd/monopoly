import os

import pytest

from monopoly.gmail.extract import Attachment
from monopoly.main import persist_attachment_to_disk


@pytest.fixture
def sample_attachment():
    return Attachment(name="test.pdf", file_byte_string=b"Test data")


def test_temporary_file_create_and_cleanup(sample_attachment):
    """
    Test that file exists during context manager, and is
    cleaned up after the context manager closes
    """
    with persist_attachment_to_disk(sample_attachment) as temp_file_path:
        assert os.path.exists(temp_file_path)

    assert not os.path.exists(temp_file_path)


def test_persist_attachment_to_disk_writes_correct_data(sample_attachment):
    """
    Test that correct data is written to file
    """
    with persist_attachment_to_disk(sample_attachment) as temp_file_path:
        with open(temp_file_path, "rb") as file:
            file_contents = file.read()
            assert file_contents == sample_attachment.file_byte_string


def test_persist_attachment_to_disk_exception_cleanup(sample_attachment):
    """
    Test that file is deleted if an exception occurs
    """
    try:
        with persist_attachment_to_disk(sample_attachment) as temp_file_path:
            assert os.path.exists(temp_file_path)
            raise Exception("Simulating an error")
    except Exception:
        pass

    assert not os.path.exists(temp_file_path)
