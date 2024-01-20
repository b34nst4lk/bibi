from enum import StrEnum
from typing import TypeAlias, Self
from dataclasses import dataclass
from collections.abc import Iterator
from argparse import ArgumentParser

MAIN = "__MAIN__"


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
    # )


OpCodes: TypeAlias = list[tuple[Op, str | None]]


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
            col += 1  # This is to accurately capture spaces
        row += 1


class DataStack:
    def __init__(self):
        self.stack = []

    # Basic ops
    def push(self, x):
        self.stack.append(x)

    def pop(self):
        return self.stack.pop()

    def dump(self):
        print(self.pop())

    def peek(self):
        return self.stack[-1]


class Program:
    def __init__(self, program: str):
        self.namespace = {MAIN: []}
        self.program = program
        self.stack = DataStack()
        self.do_stack = DataStack()

    def lex(self, debug=True):
        current_namespace = MAIN
        next_token_is_namespace = False
        namespace_stack = []
        if_stack = []
        do_stack = []
        declaration_stack = []
        in_comment = False
        comment_list = []

        for token in tokenizer(self.program):
            word = token.word
            op_codes = self.namespace[current_namespace]
            if debug:
                print(op_codes)
                print(token)

            if next_token_is_namespace:
                assert word not in self.namespace, f"`{token}` is already defined"
                next_token_is_namespace = False
                current_namespace = word
                self.namespace[word] = []
                continue

            # Handle comments
            comment_end_error = not (
                word
                in (
                    Op.CommentEnd,
                    Op.AnnotationCommentEnd,
                )
                and not in_comment
            )
            assert (
                comment_end_error
            ), f"{Op.CommentEnd}: No matching {Op.CommentStart} found"

            if in_comment:
                if token.row > op_codes[-1].token.row:
                    comment_token = Token.merge(comment_list)
                    op_codes.append(OpCode(token=comment_token, op=Op.Comment))
                    op_codes.append(OpCode(token=None, op=Op.CommentEnd))
                    in_comment = False
                elif word == Op.CommentEnd:
                    comment_token = Token.merge(comment_list)
                    op_codes.append(OpCode(token=comment_token, op=Op.Comment))
                    op_codes.append(OpCode(token=token, op=Op.CommentEnd))
                    in_comment = False
                    continue
                else:
                    comment_list.append(token)
                    continue
            elif word in (
                Op.CommentStart,
                Op.PrintCommentStart,
                Op.AnnotationCommentStart,
            ):
                op_codes.append(OpCode(token=token, op=word))
                in_comment = True
                comment_list = []
                continue

            match word:
                # Handle namespacing
                case ":":
                    next_token_is_namespace = True
                    declaration_stack.append(token)
                    namespace_stack.append(current_namespace)

                case ";":
                    assert (
                        current_namespace != MAIN
                    ), "; can only come after a declaration of a word"
                    declaration_stack.pop()
                    current_namespace = namespace_stack.pop()

                case _ if word in self.namespace:
                    op_codes.append(
                        OpCode(
                            token=token,
                            op=Op.FuncCall,
                            val=word,
                        )
                    )
                # Handle stack operations
                case Op.Swap | Op.Dup | Op.RotateDown | Op.RotateUp | Op.Dump | Op.DumpAll:
                    op_codes.append(OpCode(token=token, op=word))

                # handle arithmetic operations
                case Op.Plus | Op.Minus | Op.Times | Op.Divide | Op.Modulo:
                    op_codes.append(OpCode(token=token, op=word))

                # Handler comparisons
                case Op.Equals | Op.GreaterThan | Op.LessThan:
                    op_codes.append(OpCode(token=token, op=word))

                # Handle conditionals
                # OpCodes for conditionals are using a stack
                # When IF is encountered, we create an IF OpCode and push it
                # onto the stack. When ELSE is encountered, we pop the previous
                # IF OpCode from the stack, and set the val of the IF OpCode to
                # position after the ELSE OpCode. The ELSE OpCode is then
                # pushed onto the stack. When THEN is encountered, the same
                # thing happens except that the THEN OpCode is not pushed onto
                # the stack

                case Op.If:
                    op_code = OpCode(token=token, op=Op.If)
                    op_codes.append(op_code)
                    if_stack.append(op_code)

                case Op.Else:
                    op_code = OpCode(token=token, op=Op.Else)
                    op_codes.append(op_code)

                    previous_op_code = if_stack.pop()
                    assert (
                        previous_op_code.op == Op.If
                    ), "ELSE must come after an IF word"
                    previous_op_code.val = len(op_codes)

                    if_stack.append(op_code)

                case Op.Then:
                    op_codes.append(OpCode(token=token, op=Op.Then))

                    previous_op_code = if_stack.pop()
                    assert previous_op_code.op in {
                        Op.If,
                        Op.Else,
                    }, "THEN must come after IF or ELSE word"
                    previous_op_code.val = len(op_codes)

                # Loops
                # OpCodes for loops are done using a stack
                # When DO is encountered, a Do OpCode is pushed into the stack
                # When a LOOP, the Do OpCode is popped from the stack, and the
                # position of the Loop OpCode is set at the val of the Do
                # OpCode
                case Op.Do:
                    op_codes.append(OpCode(token=None, op=Op.SetupDo))
                    op_code = OpCode(token=token, op=Op.Do, val=len(op_codes))
                    op_codes.append(op_code)
                    do_stack.append(op_code)

                case Op.LoopCount:
                    assert (
                        do_stack
                    ), "LoopCount can only be defined in a DO .. LOOP block"
                    op_codes.append(OpCode(token=token, op=Op.LoopCount))

                case Op.Loop:
                    previous_op_code = do_stack.pop()
                    assert (
                        previous_op_code.op == Op.Do
                    ), "LOOP must come after a DO word"

                    val = previous_op_code.val

                    op_codes.append(OpCode(token=token, op=Op.Loop, val=val))
                    previous_op_code.val = len(op_codes)

                # Assume that everything else falls under push
                case _:
                    assert word.isnumeric(), (
                        f"Expecting an integer, received `{word}` instead."
                        "Non-integers are currently not supported"
                    )
                    op_codes.append(
                        OpCode(
                            token=token,
                            op=Op.Push,
                            val=int(word),
                        )
                    )

    def simulate(self, op_codes: list[OpCode] | None = None, debug=False):
        op_codes = op_codes or self.namespace[MAIN]
        pos = 0
        while pos < len(op_codes):
            op = op_codes[pos]
            if debug:
                print(self.stack.stack)
                print(op)
            match op.op:
                # Operations
                case Op.Plus:
                    self.stack.push(self.stack.pop() + self.stack.pop())
                case Op.Minus:
                    self.stack.push(self.stack.pop() - self.stack.pop())
                case Op.Times:
                    self.stack.push(self.stack.pop() * self.stack.pop())
                case Op.Divide:
                    self.stack.push(self.stack.pop() / self.stack.pop())

                # Comparisons
                case Op.Equals:
                    self.stack.push(int(self.stack.pop() == self.stack.pop()))

                case Op.GreaterThan:
                    # (a b -- flag:a>b)
                    a = self.stack.pop()
                    b = self.stack.pop()
                    self.stack.push(int(a > b))

                case Op.LessThan:
                    # (a b -- flag:a>b)
                    a = self.stack.pop()
                    b = self.stack.pop()
                    self.stack.push(int(a < b))

                # Push
                case Op.Dup:
                    top = self.stack.pop()
                    self.stack.push(top)
                    self.stack.push(top)
                case Op.Swap:
                    first, second = self.stack.pop(), self.stack.pop()
                    self.stack.push(first)
                    self.stack.push(second)
                case Op.RotateDown:
                    # (a b c -- c a b)
                    first, second, third = (
                        self.stack.pop(),
                        self.stack.pop(),
                        self.stack.pop(),
                    )
                    self.stack.push(second)
                    self.stack.push(first)
                    self.stack.push(third)
                case Op.RotateUp:
                    # (a b c -- b c a)
                    first, second, third = (
                        self.stack.pop(),
                        self.stack.pop(),
                        self.stack.pop(),
                    )
                    self.stack.push(first)
                    self.stack.push(third)
                    self.stack.push(second)
                case Op.Push:
                    assert isinstance(op.val, int)
                    self.stack.push(op.val)

                # Printing
                case Op.Dump:
                    self.stack.dump()
                case Op.DumpAll:
                    while self.stack.stack:
                        self.stack.dump()

                # Print strings
                case Op.PrintCommentStart:
                    pos += 1
                    print(op_codes[pos].token.word)

                # Conditionals
                case Op.If:
                    if not self.stack.pop():
                        pos = op.val
                        continue
                case Op.Else:
                    pos = op.val
                    continue
                case Op.Then:
                    pass  # Do nothing

                # Loop
                case Op.SetupDo:
                    start, end = self.stack.pop(), self.stack.pop()
                    self.do_stack.push(end)
                    self.do_stack.push(start)

                case Op.LoopCount:
                    self.stack.push(self.do_stack.peek() - 1)

                case Op.Do:
                    start, end = self.do_stack.pop(), self.do_stack.pop()
                    if start == end:
                        pos = op.val
                        continue
                    start += 1
                    self.do_stack.push(end)
                    self.do_stack.push(start)
                case Op.Loop:
                    pos = op.val
                    continue

                # Function call
                case Op.FuncCall:
                    self.simulate(self.namespace[op.val], debug=debug)
            pos += 1


if __name__ == "__main__":
    parser = ArgumentParser(description="Bibi Language Interpreter")
    parser.add_argument("file", type=str, help="Path to the program file")
    parser.add_argument(
        "--debug", action="store_true", help="Run the program in debug mode"
    )
    parser.add_argument(
        "--lex", action="store_true", help="Print the bytecode of the program"
    )
    pass

    args = parser.parse_args()

    with open(args.file, "r") as file:
        program_content = file.read()

    program = Program(program_content)

    if args.lex:
        program.lex(debug=False)
        from pprint import pprint

        pprint(program.namespace)
    else:
        program.lex(debug=args.debug)
        program.simulate(debug=args.debug)
