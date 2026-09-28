from pathlib import Path

from tag.reader import DrawioReader
from tag.builder import TransitionModelBuilder
from tag.excel_reader import ExcelReader


class Pipeline:

    @staticmethod
    def load(
        filename: str,
    ):

        path = Path(filename)

        suffix = path.suffix.lower()

        if suffix == ".drawio":
            reader = DrawioReader(
                filename
            )

            document = reader.read()

            builder = TransitionModelBuilder()

            return builder.build(
                document
            )

        if suffix == ".xlsx":
            return ExcelReader.read(
                filename
            )

        raise ValueError(
            "Unsupported input file type "
            f"'{path.suffix}'. "
            "Expected .drawio or .xlsx."
        )
