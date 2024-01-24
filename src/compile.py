from src.op_codes import Op, MAIN
from src.tokenizer import OpCodes

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


def compile(program: dict[str, OpCodes], f):
    f.write(PRINTS)
    f.write(STACK)

    for namespace, op_codes in program.items():
        iota = Iota()
        f.write("\n")
        scope = namespace.lower()
        if namespace == MAIN:
            f.write(f"define void @{namespace}() {{\n")
            # }} stupid comments to stop IDE from behaving weirdly
            f.write("entry: \n")
            f.write("    ; Initialize stack\n")
            f.write(f"    %{scope}_stack = alloca i32, i32 10, align 4 ; Allocate stack memory\n")
            f.write(f"    %{scope}_stack_ptr = alloca i32*, align 8    ; Allocate stack pointer\n")
            f.write(f"    call void @init_stack(i32* %{scope}_stack, i32 10, i32** %{scope}_stack_ptr)\n")
        else:
            f.write(f"define void @{namespace}(i32* %{scope}_stack, i32** %{scope}_stack_ptr) {{")
            # }} stupid comments to stop IDE from behaving weirdly
            f.write("entry: \n")
        for op_code in op_codes:
            f.write(f"    ; {op_code}\n")
            match op_code.op:
                case Op.Push:
                    f.write(push(op_code.token.word, f"%{scope}_stack_ptr"))
                # Operations
                case Op.Plus:
                    var1, var2, var3 = iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = add i32 {var1}, {var2}\n")
                    f.write(push(var3, f"%{scope}_stack_ptr"))

                case Op.Minus:
                    var1, var2, var3 = iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = sub i32 {var1}, {var2}\n")
                    f.write(push(var3, f"%{scope}_stack_ptr"))

                case Op.Times:
                    var1, var2, var3 = iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = mul i32 {var1}, {var2}\n")
                    f.write(push(var3, f"%{scope}_stack_ptr"))

                case Op.Divide:
                    var1, var2, var3 = iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = sdiv i32 {var1}, {var2}\n")
                    f.write(push(var3, f"%{scope}_stack_ptr"))

                # Comparisons
                case Op.Equals:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = icmp eq i32 {var1}, {var2}\n")
                    f.write(f"    {var4} = zext i1 {var3} to i32\n")
                    f.write(push(var4, f"%{scope}_stack_ptr"))

                case Op.GreaterThan:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = icmp sgt i32 {var1}, {var2}\n")
                    f.write(f"    {var4} = zext i1 {var3} to i32\n")
                    f.write(push(var4, f"%{scope}_stack_ptr"))

                case Op.LessThan:
                    var1, var2, var3, var4 = iota(), iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(f"    {var3} = icmp slt i32 {var1}, {var2}\n")
                    f.write(f"    {var4} = zext i1 {var3} to i32\n")
                    f.write(push(var4, f"%{scope}_stack_ptr"))

                # Push
                case Op.Dup:
                    var1 = iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(push(var1, f"%{scope}_stack_ptr"))

                case Op.Swap:
                    var1, var2 = iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(push(var1, f"%{scope}_stack_ptr"))
                    f.write(push(var2, f"%{scope}_stack_ptr"))

                case Op.RotateDown:
                    var1, var2, var3 = iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(pop(var3, f"%{scope}_stack_ptr"))
                    f.write(push(var2, f"%{scope}_stack_ptr"))
                    f.write(push(var1, f"%{scope}_stack_ptr"))
                    f.write(push(var3, f"%{scope}_stack_ptr"))

                case Op.RotateUp:
                    var1, var2, var3 = iota(), iota(), iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(pop(var2, f"%{scope}_stack_ptr"))
                    f.write(pop(var3, f"%{scope}_stack_ptr"))
                    f.write(push(var1, f"%{scope}_stack_ptr"))
                    f.write(push(var3, f"%{scope}_stack_ptr"))
                    f.write(push(var2, f"%{scope}_stack_ptr"))

                # Printing
                case Op.Dump:
                    var1 = iota()
                    f.write(pop(var1, f"%{scope}_stack_ptr"))
                    f.write(f"    call void @print_int(i32 {var1})\n")
                case Op.DumpAll:
                    raise NotImplementedError
                # Print strings
                case Op.PrintCommentStart:
                    raise NotImplementedError
                # Conditionals
                case Op.If:
                    raise NotImplementedError
                case Op.Else:
                    raise NotImplementedError
                case Op.Then:
                    raise NotImplementedError

                # Loop
                case Op.SetupDo:
                    raise NotImplementedError
                case Op.LoopCount:
                    raise NotImplementedError
                case Op.Do:
                    raise NotImplementedError
                case Op.Loop:
                    raise NotImplementedError

                # Function call
                case Op.FuncCall:
                    f.write(f"    call void @{op_code.token.word}(i32* %{scope}_stack, i32** %{scope}_stack_ptr)\n")
            f.write(f"    ; END {op_code.op.name}\n")

        f.write("    ret void\n")
        f.write("}\n")
