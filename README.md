# Resources
- [Porth](https://www.youtube.com/playlist?list=PLpM-Dvs8t0VbMZA7wW9aR3EtBqe2kinu4) - Tsoding's
livestream series on building a stack based programming language
- ["Concatenative programming and stack-based languages" by Douglas Creager](https://www.youtube.com/watch?v=umSuLpjFUf8)

# Introduction

`bibi` is a stack based toy programming language inspired by Forth.

# Usage
Python 3.10 or above is required.

1. **Installation**: Clone the repository or download the source code.
2. **Writing a Program**: Create a `.bibi` file with your Bibi language code.
3. **Running the Interpreter**:
   - To execute a Bibi program: `python bibi_interpreter.py path/to/your_program.bibi`
   - To run in debug mode (verbose output): `python bibi_interpreter.py path/to/your_program.bibi --debug`
   - To print the bytecode of the program: `python bibi_interpreter.py path/to/your_program.bibi --lex`

# Example program
The following example implements a function that derives the n-th fibonacci number:
```forth
: FIB
    : GREATER_THAN_1 DUP 1 < ;
    : MINUS_2_FROM_TOP 2 SWAP - ;
    GREATER_THAN_1 IF
        MINUS_2_FROM_TOP
        0 1
        ROT 0 DO
            DUP
            ROT
            +
        LOOP
    THEN
;

10 FIB .
```


# Language reference
As a stack based language, all operations and calculations are oriented around the stack. The code is
interpreted and executed from left to right in sequence.

## Stack effects
Stack effects annotation represents what happens at the top of the stack. The annotation follows the structure
`(: [token_1 ... token_n] -- [token_1 ... token_n] :)`. The brackets `(: ... :)` denote that this is a stack effects
annotation, and ` -- ` delimits the before and after. You can have 0 or more elements on either side of ` -- `.

Pushing a single integer onto the stack, for example, is annotated with `(: -- x )`, and a pop can be respresented by
`(: x -- :)`

## Comments

### Inline comments
Comments are written between round brackets.
```
( I am a program )
```

Unlike other languages, `bibi` allows comments to be sit between code. The following snippet shows
- 10 and 5 being pushed to the stack,
- a comment, followed by
- popping the top 2 items off the stack and adding them together before pushing them on the stack
```
10 5 ( Push 10 and 5 on the stack ) +
```

### Print function
Strings and comments can be printed out by replacing `(` with `.(`.

```
.( this comment will be printed )
    ( stdout: this comment will be printed )
```

### Annotation
Stack effects annotations represent the state of the top of the stack before and after some operation,
and can be annotated by replacing `(` and `)` with `(:` and `:)`. Here are some examples

```
(: x -- x x :)      ( The top item of the stack is duplicated )
(: x -- x' :)       ( The top item of the stack is modified )
(: x y -- y x :)    ( The top 2 items of the stack are swapped )
```

While we explicitly used `x`, `x'` and `y` in the above examples., the actual words used do not matter, so we can have
something funny like

```
(: monkey gorilla -- a_whole_zoo :) ( the top 2 elements are replaced by 1 new element )
```

## Integers

Writing an integer will push the integer onto the stack.

```
1
    ( Stack: 1 )
```

## Arithmetic operations

Basic mathematical operations can be done with `+`, `-`, `*`, `/` and `%`. Unlike most languages where
the operator sits between two operands (i.e. `a + b`), the operator indicates that it will perform
the operation over a predefined number of items off the top of the stack. The stack effects
annotation for the 4 basic operators are `(: x y -- z :)`

```
1
    ( Stack: 1 )
2
    ( Stack: 1 2 )
+
    ( Stack: 3 )
```

## Stack operations

Apart from the basic pop and push operations, the following operations combine the two to allow
convenient control of the stack

### DUP `(: x -- x x :)`
Duplicate the top item of the stack twice

```
1
    ( Stack: 1 )
DUP
    ( Stack: 1 1 )
```

### SWAP `(: x y -- y x :)`
Swap the first two items of the stack
```
1 2
    ( Stack: 1 2 )
SWAP
    ( Stack: 2 1 )
```

###  ROT `(: x y z -- y z x :)`
Rotates the top three items downwards so that the bottom of the 3 is now at the top
```
1 2 3
    ( Stack: 1 2 3 )
ROT
    ( Stack: 2 3 1 )
```

### -ROT `(: x y z -- z x y :)`
Rotates the top three items upwards so that the top of the 3 is now at the bottom
```
1 2 3
    ( Stack: 1 2 3 )
-ROT
    ( Stack: 3 1 2 )
```

### . `(: x -- :)`
Pops the top item of the stack and prints it

```
1
    ( Stack: 1)
.
    ( Stack: <empty> ; stdout: 1)
```

## Comparison operations
`>`, `<` and `=` compares the top 2 items, and pushes `1` to the top if true, and
`0` if false.
```
10 20
    ( Stack: 10 20 )
<   ( Checks if the top item of the stack is greater than the second item on the stack)
    ( Stack: 1 )
```

## Conditionals
Conditionals and code branching can be done using `.. IF .. ELSE .. THEN` blocks.

### IF `(: x -- :)`
`IF` pops the first item of the stack. If the value is `1` it continues execution until it encounters*
a `ELSE` block. However, if the first item of the stack is `0`, we jump to the first operation after `ELSE`
and continue.

### ELSE `(: -- :)`
`ELSE` does nothing to the stack. If the interpreter encounters this block, it will jump to the operation
after the `THEN` block.

### THEN `(: -- :)`
`THEN` also does nothing ot the stack. If the interpreter encounters a `THEN`, it simpliy continues

### Example
```
10 20
    ( Stack: 10 20 )
>   ( check if top item is less than second item )
    ( Stack: 0 )
IF 10 .
    ( Stack: <empty> ; Since previous item is false, we jump to operation after ELSE)
ELSE
    ( Stack: <empty> )
20
    ( Stack: 20 )
.
    ( Stack: <empty> ; stdout: 20)
```

## Loops
Bibi provides looping constructs to perform repetitive operations. The primary looping construct in Bibi is the
`DO...LOOP` structure.

### ... DO ... LOOP `(: end start -- :)`
The DO...LOOP construct in Bibi allows for executing a sequence of operations repeatedly for a specified number
of times. This loop structure is unique to stack-based languages, as it manages the loop counter separately from
the main stack.

Here's how the DO...LOOP works:

- *Initialization*: Two integers are required on the top of the stack before the DO keyword. These integers specify the start and end values for the loop counter. The top value is the end value (exclusive), and the second value is the start value.
- *Execution*: After DO, the loop starts executing from the start value up to, but not including, the end value. The operations between DO and LOOP are executed for each iteration.
- *Termination*: The loop ends when the counter reaches the end value. The LOOP keyword marks the end of the loop block.

```
0                ( Stack: 0 - accumulator for the sum )
5 0              ( Stack: 0 5 1 - set up the loop for 0 to 4 )
DO               ( Start the loop )
    LOOP_COUNT   ( Duplicate the top value, which is our loop counter )
    +            ( Add it to our accumulator )
LOOP             ( End of the loop block; after the loop, the stack has the sum )
.                ( Output the sum, which is 10 )
```

In this example, the DO...LOOP structure iterates from 0 to 4. In each iteration, it pushes the current loop count on the stack
(0, 1, 2, 3, 4) and adds it to an accumulator initialized to 0. After the loop completes, the sum (10) is left on the stack
and is then output.

## Functions
Functions are declared in the following format.
```
: function_name [sequence of operations] ;
```

`:` denotes the start of function, and `;` is the end of the function. Here's an example
of 2 functions that checks if a number is even or odd, but does not remvoe the input from
the stack

```
: is_odd (: x -- x flag :) DUP 2 % 1 = ;
: is_even (: x -- x flag :) DUP 2 % 0 = ;

10
    ( Stack: 10 )
is_odd ( function is called simply by providing the function name)
    ( Stack: 10 0 )
```

As you can see, functions in a stack based language assumes that the parameters it needs
can be found from the top of the stack.
