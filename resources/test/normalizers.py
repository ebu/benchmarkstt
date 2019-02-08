
class Testnormalizer:
    @staticmethod
    def normalize(text: str) -> str:
        return '[%s]' % (text,)
