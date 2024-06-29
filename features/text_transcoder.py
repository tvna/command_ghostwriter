from io import BytesIO
from typing import Final, Optional

import nkf


class TextTranscoder:
    def __init__(self: "TextTranscoder", input_data: BytesIO) -> None:
        self.__input_data: Final[BytesIO] = input_data
        self.__filename: Final[str] = input_data.name

    def detect_binary(self: "TextTranscoder", input_data: BytesIO) -> bool:
        current_position = input_data.tell()
        input_data.seek(0)
        chunk = input_data.read(1024)
        input_data.seek(current_position)

        return b"\0" in chunk

    def detect_encoding(self: "TextTranscoder", input_data: BytesIO) -> Optional[str]:
        if self.detect_binary(input_data):
            return None

        input_data.seek(0)
        raw_data = input_data.getvalue()
        result = nkf.guess(raw_data)  # type: ignore

        return result

    def to_utf8(self: "TextTranscoder") -> Optional[BytesIO]:
        encoding = self.detect_encoding(self.__input_data)

        if not encoding:
            return None

        try:
            self.__input_data.seek(0)
            content = self.__input_data.read().decode(encoding)
        except UnicodeDecodeError:
            return None

        output_data = BytesIO(content.encode("utf-8"))
        output_data.name = self.__filename

        return output_data

    def challenge_to_utf8(self: "TextTranscoder") -> BytesIO:
        result = self.to_utf8()

        return result if isinstance(result, BytesIO) else self.__input_data
