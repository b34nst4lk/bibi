from typing import Self
from dataclasses import dataclass
from collections.abc import Iterator

from src.op_codes import Op


@dataclass
class Token:
    word: str
    col: int
    row: int

    @classmethod
    def merge_2(cls, token_1: Self, token_2: Self) -> Self:
        word_1 = token_1.word
        word_2 = token_2.word
        spaces_between = " " * (token_2.col - len(word_1) - token_1.col)
        return Token(
            word=word_1 + spaces_between + word_2,
            col=token_1.col,
            row=token_1.row,
        )

    @classmethod
    def merge(cls, tokens: list[Self]) -> Self | None:
        if not tokens:
            return None
        final_token = tokens[0]
        for token in tokens[1:]:
            final_token = cls.merge_2(final_token, token)

        return final_token


@dataclass
class OpCode:
    token: Token | None
    op: Op
    val: str | None = None


def tokenizer(s: str) -> Iterator[Token]:
    row = 1
    for line in s.split("\n"):
        col = 1
        for word in line.split(" "):
            match word:
                case "":
                    col + 1
                case _:
                    yield Token(word, col, row)
                    col += len(word)
            # As " ".split() returns ["", ""], we need to increment the column
            # to handle column count accurately
            col += 1
        row += 1
