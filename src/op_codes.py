from enum import StrEnum
from typing import TypeAlias


class Op(StrEnum):
    Push = "PUSH"
    Pop = "POP"
    Dup = "DUP"
    Swap = "SWAP"
    RotateDown = "ROT"
    RotateUp = "-ROT"
    Dump = "."
    DumpAll = ".."

    Plus = "+"
    Minus = "-"
    Times = "*"
    Divide = "/"
    Modulo = "%"

    FuncCall = "..."  # This is used for executing words

    Equals = "="
    GreaterThan = ">"
    LessThan = "<"

    If = "IF"
    Else = "ELSE"
    Then = "THEN"

    SetupDo = "_SETUP_DO"
    Do = "DO"
    Loop = "LOOP"
    LoopCount = "LOOP_COUNT"

    PrintCommentStart = ".("
    CommentStart = "("
    CommentEnd = ")"
    Comment = "(...)"

    AnnotationCommentStart = "(:"
    AnnotationCommentEnd = ":)"
    # ) Useless comment added because the open brackets keep messing with my indentation


OpCodes: TypeAlias = list[tuple[Op, str | None]]


MAIN = "__MAIN__"
