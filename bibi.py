from argparse import ArgumentParser
from pprint import pprint

from src.compile import compile
from src.simulate import simulate
from src.lexer import lex
from src.tokenizer import tokenizer


if __name__ == "__main__":
    parser = ArgumentParser(description="Bibi Language Interpreter")
    parser.add_argument("file", type=str, help="Path to the program file")
    parser.add_argument(
        "--debug", action="store_true", help="Run the program in debug mode"
    )
    parser.add_argument(
        "--lex", action="store_true", help="Print the bytecode of the program"
    )
    parser.add_argument(
        "--compile", action="store_false", help="Compiles the program to LLVM IR"
    )

    args = parser.parse_args()

    with open(args.file, "r") as file:
        program_content = file.read()

    tokens = tokenizer(program_content)

    program = lex(tokens=tokens, debug=False)
    if args.lex:

        print("===================== LEX ====================\n")
        pprint(program)
    if args.compile:
        with open("output.ll", "w") as f:
            compile(program, f)
    else:
        if args.debug:
            print("===================== LEX ====================\n")
        program = lex(tokens=tokens, debug=args.debug)
        if args.debug:
            print("\n\n===================== SIMULATE ====================")

        simulate(program=program, debug=args.debug)
