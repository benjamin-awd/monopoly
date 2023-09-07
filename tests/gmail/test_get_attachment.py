from monopoly.gmail import Message


def test_message_with_parts(message: Message):
    data = {
        "payload": {
            "parts": [
                {
                    "partId": "1",
                    "filename": "file1.txt",
                    "body": {"attachmentId": "123"},
                },
                {"partId": "2", "body": {"attachmentId": "456"}},
            ]
        }
    }
    message.payload = data["payload"]
    parts = message.parts

    assert len(parts) == 2

    part1, part2 = parts
    assert part1.part_id == "1"
    assert part1.filename == "file1.txt"
    assert part1.attachment_id == "123"

    assert part2.part_id == "2"
    assert part2.filename is None
    assert part2.attachment_id == "456"


def test_message_with_nested_parts(message: Message):
    data = {
        "payload": {
            "parts": [
                {
                    "partId": "1",
                    "filename": "file1.txt",
                    "body": {"attachmentId": "123"},
                },
                {
                    "partId": "2",
                    "body": {"attachmentId": "456"},
                    "parts": [
                        {
                            "partId": "3",
                            "filename": "file2.txt",
                            "body": {"attachmentId": "789"},
                        }
                    ],
                },
            ]
        }
    }
    message.payload = data["payload"]
    parts = message.parts

    assert len(parts) == 3

    part1, part2, nested_part = parts
    assert part1.part_id == "1"
    assert part1.filename == "file1.txt"
    assert part1.attachment_id == "123"

    assert part2.part_id == "2"
    assert part2.filename is None
    assert part2.attachment_id == "456"

    assert nested_part.part_id == "3"
    assert nested_part.filename == "file2.txt"
    assert nested_part.attachment_id == "789"
