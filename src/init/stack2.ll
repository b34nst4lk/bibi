; Function to print an integer
@int_format = private constant [3 x i8] c"%d\0A"
declare i32 @printf(i8*, ...)

define void @print_int(i32 %val) {
entry:
    %format_str = getelementptr inbounds [3 x i8], [3 x i8]* @int_format, i32 0, i32 0
    call i32 (i8*, ...) @printf(i8* %format_str, i32 %val)
    ret void
}


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

define void @dump(i32** %stackptr) {
entry:
    %popped_value = call i32 @pop(i32** %stackptr)
    call void @print_int(i32 %popped_value)

    ret void
}

define void @plus(i32* %stack, i32** %stackptr) {
    %1 = call i32 @pop(i32** %stackptr)
    %2 = call i32 @pop(i32** %stackptr)
    %3 = add i32 %1, %2
    call void @push(i32* %stack, i32** %stackptr , i32 %3)

    ret void
}

define void @minus(i32* %stack, i32** %stackptr) {
    %1 = call i32 @pop(i32** %stackptr)
    %2 = call i32 @pop(i32** %stackptr)
    %3 = sub i32 %1, %2
    call void @push(i32* %stack, i32** %stackptr , i32 %3)

    ret void
}

define void @times(i32* %stack, i32** %stackptr) {
    %1 = call i32 @pop(i32** %stackptr)
    %2 = call i32 @pop(i32** %stackptr)
    %3 = mul i32 %1, %2
    call void @push(i32* %stack, i32** %stackptr , i32 %3)

    ret void
}

define void @divide(i32* %stack, i32** %stackptr) {
    %1 = call i32 @pop(i32** %stackptr)
    %2 = call i32 @pop(i32** %stackptr)
    %3 = sdiv i32 %1, %2
    call void @push(i32* %stack, i32** %stackptr , i32 %3)

    ret void
}



; Example usage with externally allocated stack
define i32 @main() {
entry:
    %stack_mem = alloca i32, i32 10, align 4 ; Allocate stack memory
    %stack_ptr = alloca i32*, align 8       ; Allocate stack pointer
    call void @init_stack(i32* %stack_mem, i32 10, i32** %stack_ptr)
    call void @push(i32* %stack_mem, i32** %stack_ptr, i32 10)
    call void @push(i32* %stack_mem, i32** %stack_ptr, i32 20)


    %stack_mem2 = alloca i32, i32 10, align 4 ; Allocate stack 2 memory
    %stack_ptr2 = alloca i32*, align 8       ; Allocate stack 2 pointer
    call void @init_stack(i32* %stack_mem2, i32 10, i32** %stack_ptr2)
    call void @push(i32* %stack_mem2, i32** %stack_ptr2 , i32 2)
    call void @push(i32* %stack_mem2, i32** %stack_ptr2 , i32 10)
    call void @plus(i32* %stack_mem2, i32** %stack_ptr2)
    call void @dump(i32** %stack_ptr2)

    call void @push(i32* %stack_mem2, i32** %stack_ptr2 , i32 210)
    call void @push(i32* %stack_mem2, i32** %stack_ptr2 , i32 330)

    call void @dump(i32** %stack_ptr)
    call void @dump(i32** %stack_ptr)
    call void @plus(i32* %stack_mem2, i32** %stack_ptr2)
    call void @minus(i32* %stack_mem2, i32** %stack_ptr2)
    call void @times(i32* %stack_mem2, i32** %stack_ptr2)
    call void @divide(i32* %stack_mem2, i32** %stack_ptr2)

    call void @dump(i32** %stack_ptr2)

    ret i32 0
}
