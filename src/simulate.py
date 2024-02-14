from src.op_codes import Op, MAIN
from src.stack import Stack
from src.tokenizer import OpCodes


def simulate(
    program: dict[str, OpCodes],
    namespace: str = MAIN,
    main_stack: Stack | None = None,
    do_stack: Stack | None = None,
    debug: bool = False,
):
    op_codes = program[namespace]
    main_stack = Stack() if main_stack is None else main_stack
    do_stack = Stack() if do_stack is None else do_stack
    pos = 0
    while pos < len(op_codes):
        op = op_codes[pos]
        if debug:
            print(main_stack.stack)
            print(op)
        match op.op:
            # Operations
            case Op.Plus:
                main_stack.push(main_stack.pop() + main_stack.pop())
            case Op.Minus:
                main_stack.push(main_stack.pop() - main_stack.pop())
            case Op.Times:
                main_stack.push(main_stack.pop() * main_stack.pop())
            case Op.Divide:
                main_stack.push(main_stack.pop() / main_stack.pop())

            # Comparisons
            case Op.Equals:
                main_stack.push(int(main_stack.pop() == main_stack.pop()))

            case Op.GreaterThan:
                # (a b -- flag:a>b)
                a = main_stack.pop()
                b = main_stack.pop()
                main_stack.push(int(a > b))

            case Op.LessThan:
                # (a b -- flag:a>b)
                a = main_stack.pop()
                b = main_stack.pop()
                main_stack.push(int(a < b))

            # Push
            case Op.Dup:
                top = main_stack.pop()
                main_stack.push(top)
                main_stack.push(top)
            case Op.Swap:
                first, second = main_stack.pop(), main_stack.pop()
                main_stack.push(first)
                main_stack.push(second)
            case Op.RotateDown:
                # (a b c -- c a b)
                first, second, third = (
                    main_stack.pop(),
                    main_stack.pop(),
                    main_stack.pop(),
                )
                main_stack.push(second)
                main_stack.push(first)
                main_stack.push(third)
            case Op.RotateUp:
                # (a b c -- b c a)
                first, second, third = (
                    main_stack.pop(),
                    main_stack.pop(),
                    main_stack.pop(),
                )
                main_stack.push(first)
                main_stack.push(third)
                main_stack.push(second)
            case Op.Push:
                assert isinstance(op.val, int)
                main_stack.push(op.val)

            # Printing
            case Op.Dump:
                print(main_stack.pop())
            case Op.DumpAll:
                while main_stack.stack:
                    print(main_stack.pop())

            # Print strings
            case Op.PrintCommentStart:
                pos += 1
                print(op_codes[pos].token.word)

            # Conditionals
            case Op.If:
                if not main_stack.pop():
                    pos = op.val
                    continue
            case Op.Else:
                pos = op.val
                continue
            case Op.Then:
                pass  # Do nothing

            # Loop
            case Op.SetupDo:
                start, end = main_stack.pop(), main_stack.pop()
                do_stack.push(end)
                do_stack.push(start)

            case Op.LoopCount:
                main_stack.push(do_stack.peek() - 1)

            case Op.Do:
                start, end = do_stack.pop(), do_stack.pop()
                if start == end:
                    pos = op.val
                    continue
                start += 1
                do_stack.push(end)
                do_stack.push(start)
            case Op.Loop:
                pos = op.val
                continue

            # Function call
            case Op.FuncCall:
                simulate(
                    program=program,
                    namespace=op.val,
                    main_stack=main_stack,
                    do_stack=do_stack,
                    debug=debug,
                )
        pos += 1
