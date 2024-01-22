; ModuleID = 'stack.c'
source_filename = "stack.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx14.0.0"

%struct.Stack = type { [10 x i32], i32 }

@.str = private unnamed_addr constant [12 x i8] c"Popped: %d\0A\00", align 1
@.str.1 = private unnamed_addr constant [18 x i8] c"Stack Underflow!\0A\00", align 1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @initializeStack(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %struct.Stack, ptr %3, i32 0, i32 1
  store i32 -1, ptr %4, align 4
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define zeroext i1 @isFull(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %struct.Stack, ptr %3, i32 0, i32 1
  %5 = load i32, ptr %4, align 4
  %6 = icmp eq i32 %5, 9
  ret i1 %6
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define zeroext i1 @isEmpty(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %struct.Stack, ptr %3, i32 0, i32 1
  %5 = load i32, ptr %4, align 4
  %6 = icmp eq i32 %5, -1
  ret i1 %6
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define zeroext i1 @push(ptr noundef %0, i32 noundef %1) #0 {
  %3 = alloca i1, align 1
  %4 = alloca ptr, align 8
  %5 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store i32 %1, ptr %5, align 4
  %6 = load ptr, ptr %4, align 8
  %7 = call zeroext i1 @isFull(ptr noundef %6)
  br i1 %7, label %8, label %9

8:                                                ; preds = %2
  store i1 false, ptr %3, align 1
  br label %19

9:                                                ; preds = %2
  %10 = load i32, ptr %5, align 4
  %11 = load ptr, ptr %4, align 8
  %12 = getelementptr inbounds %struct.Stack, ptr %11, i32 0, i32 0
  %13 = load ptr, ptr %4, align 8
  %14 = getelementptr inbounds %struct.Stack, ptr %13, i32 0, i32 1
  %15 = load i32, ptr %14, align 4
  %16 = add nsw i32 %15, 1
  store i32 %16, ptr %14, align 4
  %17 = sext i32 %16 to i64
  %18 = getelementptr inbounds [10 x i32], ptr %12, i64 0, i64 %17
  store i32 %10, ptr %18, align 4
  store i1 true, ptr %3, align 1
  br label %19

19:                                               ; preds = %9, %8
  %20 = load i1, ptr %3, align 1
  ret i1 %20
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define zeroext i1 @pop(ptr noundef %0, ptr noundef %1) #0 {
  %3 = alloca i1, align 1
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  %6 = load ptr, ptr %4, align 8
  %7 = call zeroext i1 @isEmpty(ptr noundef %6)
  br i1 %7, label %8, label %9

8:                                                ; preds = %2
  store i1 false, ptr %3, align 1
  br label %20

9:                                                ; preds = %2
  %10 = load ptr, ptr %4, align 8
  %11 = getelementptr inbounds %struct.Stack, ptr %10, i32 0, i32 0
  %12 = load ptr, ptr %4, align 8
  %13 = getelementptr inbounds %struct.Stack, ptr %12, i32 0, i32 1
  %14 = load i32, ptr %13, align 4
  %15 = add nsw i32 %14, -1
  store i32 %15, ptr %13, align 4
  %16 = sext i32 %14 to i64
  %17 = getelementptr inbounds [10 x i32], ptr %11, i64 0, i64 %16
  %18 = load i32, ptr %17, align 4
  %19 = load ptr, ptr %5, align 8
  store i32 %18, ptr %19, align 4
  store i1 true, ptr %3, align 1
  br label %20

20:                                               ; preds = %9, %8
  %21 = load i1, ptr %3, align 1
  ret i1 %21
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @testStack() #0 {
  %1 = alloca %struct.Stack, align 4
  %2 = alloca i32, align 4
  call void @initializeStack(ptr noundef %1)
  %3 = call zeroext i1 @push(ptr noundef %1, i32 noundef 10)
  %4 = call zeroext i1 @push(ptr noundef %1, i32 noundef 20)
  %5 = call zeroext i1 @push(ptr noundef %1, i32 noundef 30)
  %6 = call zeroext i1 @pop(ptr noundef %1, ptr noundef %2)
  br i1 %6, label %7, label %10

7:                                                ; preds = %0
  %8 = load i32, ptr %2, align 4
  %9 = call i32 (ptr, ...) @printf(ptr noundef @.str, i32 noundef %8)
  br label %10

10:                                               ; preds = %7, %0
  %11 = call zeroext i1 @pop(ptr noundef %1, ptr noundef %2)
  br i1 %11, label %12, label %15

12:                                               ; preds = %10
  %13 = load i32, ptr %2, align 4
  %14 = call i32 (ptr, ...) @printf(ptr noundef @.str, i32 noundef %13)
  br label %15

15:                                               ; preds = %12, %10
  %16 = call zeroext i1 @pop(ptr noundef %1, ptr noundef %2)
  br i1 %16, label %17, label %20

17:                                               ; preds = %15
  %18 = load i32, ptr %2, align 4
  %19 = call i32 (ptr, ...) @printf(ptr noundef @.str, i32 noundef %18)
  br label %20

20:                                               ; preds = %17, %15
  %21 = call zeroext i1 @pop(ptr noundef %1, ptr noundef %2)
  br i1 %21, label %24, label %22

22:                                               ; preds = %20
  %23 = call i32 (ptr, ...) @printf(ptr noundef @.str.1)
  br label %24

24:                                               ; preds = %22, %20
  ret void
}

declare i32 @printf(ptr noundef, ...) #1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define i32 @main() #0 {
  %1 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  call void @testStack()
  ret i32 0
}

attributes #0 = { noinline nounwind optnone ssp uwtable(sync) "frame-pointer"="non-leaf" "min-legal-vector-width"="0" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 14, i32 2]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 1}
!5 = !{!"Apple clang version 15.0.0 (clang-1500.1.0.2.5)"}
