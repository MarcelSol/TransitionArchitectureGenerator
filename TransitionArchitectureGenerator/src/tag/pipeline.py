from tag.builder import TransitionModelBuilder
from tag.reader import DrawioReader


class Pipeline:

    @staticmethod
    def load(filename: str):

        reader = DrawioReader(filename)

        document = reader.read()

        builder = TransitionModelBuilder()

        return builder.build(document)
