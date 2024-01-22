#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define STACK_MAX_SIZE 10

typedef struct {
    int32_t data[STACK_MAX_SIZE];
    int top;
} Stack;

void initializeStack(Stack *stack) {
    stack->top = -1;
}

bool isFull(Stack *stack) {
    return stack->top == STACK_MAX_SIZE - 1;
}

bool isEmpty(Stack *stack) {
    return stack->top == -1;
}

bool push(Stack *stack, int32_t value) {
    if (isFull(stack)) {
        return false;
    }
    stack->data[++stack->top] = value;
    return true;
}

bool pop(Stack *stack, int32_t *value) {
    if (isEmpty(stack)) {
        return false;
    }
    *value = stack->data[stack->top--];
    return true;
}

// Test cases for the stack
void testStack() {
    Stack stack;
    initializeStack(&stack);

    // Test pushing items
    push(&stack, 10);
    push(&stack, 20);
    push(&stack, 30);

    // Test popping items
    int32_t value;
    if (pop(&stack, &value)) {
        printf("Popped: %d\n", value); // Should be 30
    }
    if (pop(&stack, &value)) {
        printf("Popped: %d\n", value); // Should be 20
    }
    if (pop(&stack, &value)) {
        printf("Popped: %d\n", value); // Should be 10
    }

    // Test underflow
    if (!pop(&stack, &value)) {
        printf("Stack Underflow!\n");
    }
}

int main() {
    testStack();
    return 0;
}
