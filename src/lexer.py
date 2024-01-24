from typing import Iterable

from src.op_codes import Op, MAIN
from src.stack import Stack
from src.tokenizer import Token, OpCode, OpCodes


def lex(tokens: Iterable[Token], debug=True) -> dict[str, OpCodes]:
    namespace = {MAIN: []}
    current_namespace = MAIN
    next_token_is_namespace = False
    namespace_stack = Stack()
    if_stack = []
    do_stack = []
    declaration_stack = Stack()
    in_comment = False
    comment_list = []

    for token in tokens:
        word = token.word
        op_codes = namespace[current_namespace]
        if debug:
            print(op_codes)
            print(token)

        if next_token_is_namespace:
            assert word not in namespace, f"`{token}` is already defined"
            next_token_is_namespace = False
            current_namespace = word
            namespace[word] = []
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
            op_codes.append(OpCode(token=token, op=Op(word)))
            in_comment = True
            comment_list = []
            continue

        match word:
            # Handle namespacing
            case ":":
                next_token_is_namespace = True
                declaration_stack.push(token)
                namespace_stack.push(current_namespace)

            case ";":
                assert (
                    current_namespace != MAIN
                ), "; can only come after a declaration of a word"
                declaration_stack.pop()
                current_namespace = namespace_stack.pop()

            case _ if word in namespace:
                op_codes.append(
                    OpCode(
                        token=token,
                        op=Op.FuncCall,
                        val=word,
                    )
                )
            # Handle stack operations
            case Op.Swap | Op.Dup | Op.RotateDown | Op.RotateUp | Op.Dump | Op.DumpAll:
                op_codes.append(OpCode(token=token, op=Op(word)))

            # handle arithmetic operations
            case Op.Plus | Op.Minus | Op.Times | Op.Divide | Op.Modulo:
                op_codes.append(OpCode(token=token, op=Op(word)))

            # Handler comparisons
            case Op.Equals | Op.GreaterThan | Op.LessThan:
                op_codes.append(OpCode(token=token, op=Op(word)))

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

    return namespace
