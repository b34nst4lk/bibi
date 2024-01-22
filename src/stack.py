class StackOverflow(Exception):
    pass


class StackUnderflow(Exception):
    pass


class Stack:
    def __init__(self, maxsize=10):
        self.stack = []
        self.maxsize = maxsize

    def push(self, x):
        if len(self.stack) >= self.maxsize:
            raise StackOverflow

        self.stack.append(x)

    def pop(self):
        if len(self.stack) == 0:
            raise StackUnderflow

        return self.stack.pop()

    def peek(self):
        return self.stack[-1]
