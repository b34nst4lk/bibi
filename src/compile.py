from src.op_codes import Op, MAIN
from src.tokenizer import OpCodes
from src.stack import Stack

PRINTS = """
@overflow_error = private unnamed_addr constant [23 x i8] c"ERROR: stack overflow\\0A\\00", align 1
@underflow_error = private unnamed_addr constant [24 x i8] c"ERROR: stack underflow\\0A\\00", align 1
declare i32 @puts(i8*)

; Function to print an integer
@int_format = private constant [4 x i8] c"%d\\0A\\00"
declare i32 @printf(i8*, ...)

define void @print_int(i32 %val) {
entry:
    %format_str = getelementptr inbounds [4 x i8], [4 x i8]* @int_format, i32 0, i32 0
    call i32 (i8*, ...) @printf(i8* %format_str, i32 %val)
    ret void
}
define void @print_int64(i64 %val) {
entry:
    %format_str = getelementptr inbounds [4 x i8], [4 x i8]* @int_format, i64 0, i64 0
    call i32 (i8*, ...) @printf(i8* %format_str, i64 %val)
    ret void
}
"""


STACK = """
declare void @exit(i32 )
; Define the stack operations as functions
define void @init_stack(i32* %stack, i32 %size, i32** %stackptr) {
entry:
    %end = getelementptr i32, i32* %stack, i32 %size
    store i32* %end, i32** %stackptr, align 8
    ret void
}

define void @push(i32* %stack, i32** %stackptr, i32 %val) {
entry:
    %stack_top = load i32*, i32** %stackptr, align 8
    %new_top = getelementptr inbounds i32, i32* %stack_top, i32 -1
    %base = ptrtoint i32* %stack to i32
    %current = ptrtoint i32* %new_top to i32
    %overflow = icmp ule i32 %current, %base

    br i1 %overflow, label %overflow_label, label %push_val

overflow_label:
    call void @handle_overflow()
    unreachable

push_val:
    store i32 %val, i32* %new_top, align 4
    store i32* %new_top, i32** %stackptr, align 8
    ret void
}

define i32 @pop(i32* %stack, i32** %stackptr) {
entry:
    %stack_top = load i32*, i32** %stackptr, align 8
    %base = ptrtoint i32* %stack to i32
    %current = ptrtoint i32* %stack_top to i32
    %underflow = icmp uge i32 %current, %base

    call void @print_int(i32 %current)
    call void @print_int(i32 %base)

    br i1 %underflow, label %underflow_label, label %pop_val

underflow_label:
    call void @handle_underflow()
    unreachable

pop_val:
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

define i32 @size(i32* %stack, i32** %stackptr) {
entry:
    %stack_top = load i32*, i32** %stackptr, align 8
    %stack_base = ptrtoint i32* %stack to i64
    %stack_current = ptrtoint i32* %stack_top to i64
    %diff = sub i64 %stack_current, %stack_base
    %size = sdiv i64 %diff, 4
    %stack_size = trunc i64 %size to i32
    ret i32 %stack_size
}

define void @handle_overflow() {
entry:
    %overflow_error = getelementptr [23 x i8], [23 x i8]*  @overflow_error, i64 0, i64 0
    call i32 @puts(i8* %overflow_error)
    call void @exit(i32 -1)
    unreachable
}

define void @handle_underflow() {
entry:
    %underflow_error = getelementptr [24 x i8], [24 x i8]*  @underflow_error, i64 0, i64 0
    call i32 @puts(i8* %underflow_error)
    call void @exit(i32 -1)
    unreachable
}
"""


class Iota:
    def __init__(self, prefix=""):
        self.count = -1
        self.prefix = prefix

    def __call__(self) -> str:
        self.count += 1
        return f"{self.prefix}_{self.count}"


def pop(stack, var, pointer) -> str:
    return f"    {var} = call i32 @pop(i32* {stack}, i32** {pointer})\n"


def push(stack, var, pointer) -> str:
    return f"    call void @push(i32* {stack}, i32** {pointer} , i32 {var})\n"


def print_int(var) -> str:
    return f"    call void @print_int(i32 {var})\n"


def init_stack(scope, size=1) -> str:
    size += 1
    return f"""
    %{scope}_stack = alloca i32, i32 {size}, align 4 ; Allocate stack memory
    %{scope}_stack_ptr = alloca i32*, align 8    ; Allocate stack pointer
    call void @init_stack(i32* %{scope}_stack, i32 {size}, i32** %{scope}_stack_ptr)
    """


def define_string(var, string) -> str:
    return f'@{var} = private unnamed_addr constant [{len(string)+2} x i8] c"{string}\\0A\\00", align 1\n'


if_iota = Iota(prefix="%")
do_iota = Iota(prefix="%")
str_iota = Iota("str_")


def compile(program: dict[str, OpCodes], f):
    lines = [PRINTS, STACK]
    for namespace, op_codes in program.items():
        print_comment = False
        iota = Iota(prefix="%")
        lines.append("\n")
        scope = namespace.lower()
        if namespace == MAIN:
            lines.append(f"define void @{namespace}() {{\n")
            # }} stupid comments to stop IDE from behaving weirdly
            lines.append("entry: \n")
            lines.append("    ; Initialize stack\n")
            # main stack
            lines.append(init_stack(scope))
        else:
            lines.append(f"define void @{namespace}(i32* %{scope}_stack, i32** %{scope}_stack_ptr) {{\n")
            # }} stupid comments to stop IDE from behaving weirdly
            lines.append("entry: \n")

        block_stack = Stack()
        for op_code in op_codes:
            lines.append(f"    ; {op_code}\n")
            match op_code.op:
                case Op.Push:
                    lines.append(push(f"%{scope}_stack", op_code.token.word, f"%{scope}_stack_ptr"))

                # Math
                case Op.Plus:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = add i32 {var1}, {var2}\n")
                    lines.append(push(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))

                case Op.Minus:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = sub i32 {var1}, {var2}\n")
                    lines.append(push(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))

                case Op.Times:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = mul i32 {var1}, {var2}\n")
                    lines.append(push(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))

                case Op.Divide:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = sdiv i32 {var1}, {var2}\n")
                    lines.append(push(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))

                # Comparisons
                case Op.Equals:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = icmp eq i32 {var1}, {var2}\n")
                    lines.append(f"    {var4} = zext i1 {var3} to i32\n")
                    lines.append(print_int(var4))
                    lines.append(push(f"%{scope}_stack", var4, f"%{scope}_stack_ptr"))

                case Op.GreaterThan:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = icmp sgt i32 {var1}, {var2}\n")
                    lines.append(f"    {var4} = zext i1 {var3} to i32\n")
                    lines.append(push(f"%{scope}_stack", var4, f"%{scope}_stack_ptr"))

                case Op.LessThan:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(f"    {var3} = icmp slt i32 {var1}, {var2}\n")
                    lines.append(f"    {var4} = zext i1 {var3} to i32\n")
                    lines.append(push(f"%{scope}_stack", var4, f"%{scope}_stack_ptr"))

                # Stack ops
                case Op.Dup:
                    var1 = iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))

                case Op.Swap:
                    var1, var2 = iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))

                case Op.RotateDown:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))

                case Op.RotateUp:
                    var1, var2, var3 = iota(), iota(), iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var3, f"%{scope}_stack_ptr"))
                    lines.append(push(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))

                # Printing
                case Op.Dump:
                    var1 = iota()
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
                    lines.append(print_int(var1))
                case Op.DumpAll:
                    raise NotImplementedError
                # Print strings
                case Op.PrintCommentStart:
                    print_comment = True
                case Op.Comment:
                    if print_comment:
                        var1 = str_iota()
                        string = op_code.token.word
                        lines.insert(0, define_string(var1, string))
                        var2 = iota()
                        lines.append(f"    {var2} = getelementptr [{len(string)+2} x i8], [{len(string)+2} x i8]*  @{var1}, i64 0, i64 0\n")
                        lines.append(f"    call i32 @puts(i8* {var2})\n")
                    print_comment = False

                # Conditionals
                case Op.If:
                    var1, var2 = iota(), iota()
                    if_label = f"%if_label_{if_iota()[1:]}"
                    next_label = f"%label_{op_code.val}"
                    block_stack.push(next_label[1:])
                    lines.append(pop(f"%{scope}_stack", var1, f"%{scope}_stack_ptr"))
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
                    lines.append(pop(f"%{scope}_stack", do_start_var, f"%{scope}_stack_ptr"))
                    lines.append(pop(f"%{scope}_stack", do_end_var, f"%{scope}_stack_ptr"))

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
                    lines.append(push(f"%{scope}_stack", var2, f"%{scope}_stack_ptr"))

                case Op.Loop:
                    val = block_stack.pop().val
                    do_counter = f"%do_counter_{val}"
                    do_label = f"do_label_{val}"
                    do_end_label = f"do_block_end_{val}"
                    cond_val = f"cond_{val}"
                    current_val, next_val = iota(), iota()

                    lines.append(f"    {current_val} = load i32, i32* {do_counter}\n")
                    lines.append(f"    {next_val} = sub i32 {current_val}, 1\n")
                    lines.append(f"    store i32 {next_val}, i32* {do_counter}\n")
                    lines.append(f"    %{cond_val} = icmp sgt i32 {next_val}, 0\n")
                    lines.append(f"    br i1 %{cond_val}, label %{do_label}, label %{do_end_label}\n")

                    lines.append(f"{do_end_label}:\n")
                # # Function call
                case Op.FuncCall:
                    lines.append(f"    call void @{op_code.token.word}(i32* %{scope}_stack, i32** %{scope}_stack_ptr)\n")
            lines.append(f"    ; END {op_code.op.name}\n")

        lines.append("    ret void\n")
        lines.append("}\n")
    f.writelines(lines)
