from src.op_codes import Op, MAIN
from src.tokenizer import OpCodes
from src.stack import Stack

PRINTS = """
; Function to print an integer
@int_format = private constant [4 x i8] c"%d\\0A\\00"
declare i32 @printf(i8*, ...)

define void @print_int(i32 %val) {
entry:
    %format_str = getelementptr inbounds [4 x i8], [4 x i8]* @int_format, i32 0, i32 0
    call i32 (i8*, ...) @printf(i8* %format_str, i32 %val)
    ret void
}
"""


STACK = """
; Define the stack operations as functions
define void @init_stack(i32* %stack, i32 %size, i32** %stackptr) {
entry:
    %end = getelementptr i32, i32* %stack, i32 %size
    store i32* %end, i32** %stackptr, align 8
    ret void
}

define void @push(i32** %stackptr, i32 %val) {
entry:
    %stack_top = load i32*, i32** %stackptr, align 8
    %new_top = getelementptr inbounds i32, i32* %stack_top, i32 -1
    store i32 %val, i32* %new_top, align 4
    store i32* %new_top, i32** %stackptr, align 8
    ret void
}

define i32 @pop(i32** %stackptr) {
entry:
    %stack_top = load i32*, i32** %stackptr, align 8
    %val = load i32, i32* %stack_top, align 4
    %new_top = getelementptr inbounds i32, i32* %stack_top, i32 1
    store i32* %new_top, i32** %stackptr, align 8
    ret i32 %val
}

define void @peek(i32** %stackptr) {
entry:
    %stack_top = load i32*, i32** %stackptr, align 8
    %val = load i32, i32* %stack_top, align 4
    call void @print_int(i32 %val)
    ret void
}
"""


class Iota:
    def __init__(self):
        self.count = -1

    def __call__(self) -> str:
        self.count += 1
        return f"%{self.count}"


def pop(var, pointer) -> str:
    return f"    {var} = call i32 @pop(i32** {pointer})\n"


def push(var, pointer) -> str:
    return f"    call void @push(i32** {pointer} , i32 {var})\n"


def print_int(var) -> str:
    return f"    call void @print_int(i32 {var})\n"


if_iota = Iota()
do_iota = Iota()


def compile(program: dict[str, OpCodes], f):
    lines = [PRINTS, STACK]
    for namespace, op_codes in program.items():
        iota = Iota()
        lines.append("\n")
        scope = namespace.lower()
        if namespace == MAIN:
            lines.append(f"define void @{namespace}() {{\n")
            # }} stupid comments to stop IDE from behaving weirdly
            lines.append("entry: \n")
            lines.append("    ; Initialize stack\n")
            # main stack
            lines.append(f"    %{scope}_stack = alloca i32, i32 10, align 4 ; Allocate stack memory\n")
            lines.append(f"    %{scope}_stack_ptr = alloca i32*, align 8    ; Allocate stack pointer\n")
            lines.append(f"    call void @init_stack(i32* %{scope}_stack, i32 10, i32** %{scope}_stack_ptr)\n")
        else:
            lines.append(f"define void @{namespace}(i32* %{scope}_stack, i32** %{scope}_stack_ptr) {{\n")
            # }} stupid comments to stop IDE from behaving weirdly
            lines.append("entry: \n")

        block_stack = Stack()
        for op_code in op_codes:
            lines.append(f"    ; {op_code}\n")
            match op_code.op:
                case Op.Push:
                    lines.append(push(op_code.token.word, f"%{scope}_stack_ptr"))

                # Math
                case Op.Plus:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = add i32 {var1}, {var2}\n")
                    lines.append(push(var3, f"%{scope}_stack_ptr"))

                case Op.Minus:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = sub i32 {var1}, {var2}\n")
                    lines.append(push(var3, f"%{scope}_stack_ptr"))

                case Op.Times:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = mul i32 {var1}, {var2}\n")
                    lines.append(push(var3, f"%{scope}_stack_ptr"))

                case Op.Divide:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = sdiv i32 {var1}, {var2}\n")
                    lines.append(push(var3, f"%{scope}_stack_ptr"))

                # Comparisons
                case Op.Equals:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = icmp eq i32 {var1}, {var2}\n")
                    lines.append(f"    {var4} = zext i1 {var3} to i32\n")
                    lines.append(print_int(var4))
                    lines.append(push(var4, f"%{scope}_stack_ptr"))

                case Op.GreaterThan:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = icmp sgt i32 {var1}, {var2}\n")
                    lines.append(f"    {var4} = zext i1 {var3} to i32\n")
                    lines.append(push(var4, f"%{scope}_stack_ptr"))

                case Op.LessThan:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = icmp slt i32 {var1}, {var2}\n")
                    lines.append(f"    {var4} = zext i1 {var3} to i32\n")
                    lines.append(push(var4, f"%{scope}_stack_ptr"))

                # Stack ops
                case Op.Dup:
                    var1 = iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(push(var1, f"%{scope}_stack_ptr"))
                    lines.append(push(var1, f"%{scope}_stack_ptr"))

                case Op.Swap:
                    var1, var2 = iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(push(var1, f"%{scope}_stack_ptr"))
                    lines.append(push(var2, f"%{scope}_stack_ptr"))

                case Op.RotateDown:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(pop(var3, f"%{scope}_stack_ptr"))
                    lines.append(push(var2, f"%{scope}_stack_ptr"))
                    lines.append(push(var1, f"%{scope}_stack_ptr"))
                    lines.append(push(var3, f"%{scope}_stack_ptr"))

                case Op.RotateUp:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(var2, f"%{scope}_stack_ptr"))
                    lines.append(pop(var3, f"%{scope}_stack_ptr"))
                    lines.append(push(var1, f"%{scope}_stack_ptr"))
                    lines.append(push(var3, f"%{scope}_stack_ptr"))
                    lines.append(push(var2, f"%{scope}_stack_ptr"))

                # Printing
                case Op.Dump:
                    var1 = iota()
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(print_int(var1))
                case Op.DumpAll:
                    raise NotImplementedError
                # Print strings
                case Op.PrintCommentStart:
                    raise NotImplementedError
                # Conditionals
                case Op.If:
                    var1, var2 = iota(), iota()
                    if_label = f"%if_label_{if_iota()[1:]}"
                    next_label = f"%label_{op_code.val}"
                    block_stack.push(next_label[1:])
                    lines.append(pop(var1, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var2} = icmp eq i32 {var1}, 1\n")
                    lines.append(f"    br i1 {var2}, label {if_label}, label {next_label}\n")
                    lines.append("\n")
                    lines.append(f"{if_label[1:]}:\n")
                case Op.Else:
                    # end of if block jumps to continue block
                    lines.append(f"    br label %label_{op_code.val}\n")
                    else_label = block_stack.peek()
                    lines.append(f"{else_label}:\n")

                case Op.Then:
                    lines.append(f"    br label %label_{op_code.val}\n")
                    block_stack.pop()
                    lines.append(f"label_{op_code.val}:\n")

                # Loop
                case Op.SetupDo:

                    pass

                case Op.Do:
                    val = op_code.val
                    block_stack.push(op_code)
                    do_start_var = f"%do_start_{val}"
                    do_end_var = f"%do_end_{val}"
                    do_counter = f"%do_counter_{val}"
                    do_label = f"do_label_{val}"
                    do_counter_val = iota()
                    lines.append(pop(do_start_var, f"%{scope}_stack_ptr"))
                    lines.append(pop(do_end_var, f"%{scope}_stack_ptr"))

                    # Store counter
                    lines.append(f"    {do_counter} = alloca i32\n")
                    lines.append(f"    {do_counter_val} = sub i32 {do_end_var}, {do_start_var}\n")
                    lines.append(f"    store i32 {do_counter_val}, i32* {do_counter}\n")

                    lines.append(f"    br label %{do_label}\n")
                    lines.append(f"{do_label}:\n")

                case Op.LoopCount:
                    var1, var2 = iota(), iota()
                    val = block_stack.peek().val
                    do_counter = f"%do_counter_{val}"
                    lines.append(f"    {var1} = load i32, i32* {do_counter}\n")
                    lines.append(f"    {var2} = sub i32 %do_end_{val}, {var1}\n")
                    lines.append(push(var2, f"%{scope}_stack_ptr"))

                case Op.Loop:
                    val = block_stack.pop().val
                    do_counter = f"%do_counter_{val}"
                    do_label = f"do_label_{val}"
                    do_end_label = f"do_block_end_{val}"
                    current_val, next_val = iota(), iota()

                    lines.append(f"    {current_val} = load i32, i32* {do_counter}\n")
                    lines.append(f"    {next_val} = sub i32 {current_val}, 1\n")
                    lines.append(f"    store i32 {next_val}, i32* {do_counter}\n")
                    lines.append(f"    %cond = icmp sgt i32 {next_val}, 0\n")
                    lines.append(f"    br i1 %cond, label %{do_label}, label %{do_end_label}\n")

                    lines.append(f"{do_end_label}:\n")
                # # Function call
                case Op.FuncCall:
                    lines.append(f"    call void @{op_code.token.word}(i32* %{scope}_stack, i32** %{scope}_stack_ptr)\n")
            lines.append(f"    ; END {op_code.op.name}\n")

        lines.append("    ret void\n")
        lines.append("}\n")
    f.writelines(lines)
