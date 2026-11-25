import argparse
import re
import sys
from pathlib import Path

SYMBOL = re.compile(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*")
ROM_CAPACITY = 1 << 15
PREDEFINED = {f"R{i}": i for i in range(16)}
PREDEFINED.update(SP=0, LCL=1, ARG=2, THIS=3, THAT=4,
                  SCREEN=16384, KBD=24576)

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}
DEST = {name: f"{i:03b}" for i, name in
        enumerate(("", "M", "D", "MD", "A", "AM", "AD", "AMD"))}
JUMP = {name: f"{i:03b}" for i, name in
        enumerate(("", "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"))}


def encode_c(command):
    body, semicolon, jump = command.partition(";")
    dest, equals, comp = body.partition("=")
    if not equals:
        comp, dest = dest, ""
    if (equals and not dest) or (semicolon and not jump):
        raise ValueError("invalid C-instruction")
    try:
        return "111" + COMP[comp] + DEST[dest] + JUMP[jump]
    except KeyError:
        raise ValueError(f"invalid C-instruction {command!r}") from None


def assemble(source):
    symbols = PREDEFINED.copy()
    instructions = []

    # Pass 1. Labels point to the next instruction in ROM.
    for number, raw in enumerate(source.splitlines(), 1):
        command = "".join(raw.partition("//")[0].split())
        if not command:
            continue
        if not command.startswith("("):
            if len(instructions) >= ROM_CAPACITY:
                raise ValueError(f"Line {number}: ROM address space exhausted")
            instructions.append((number, command))
            continue
        label = command[1:-1]
        if not command.endswith(")") or not SYMBOL.fullmatch(label):
            raise ValueError(f"Line {number}: invalid label {command!r}")
        if label in symbols:
            raise ValueError(f"Line {number}: duplicate or reserved label {label!r}")
        if len(instructions) >= ROM_CAPACITY:
            raise ValueError(f"Line {number}: label address exceeds ROM capacity")
        symbols[label] = len(instructions)

    # Pass 2. Resolve symbols, allocate variables, and emit words.
    words = []
    next_ram = 16
    for number, command in instructions:
        try:
            if not command.startswith("@"):
                words.append(encode_c(command))
                continue
            token = command[1:]
            if token.isascii() and token.isdecimal():
                value = int(token)
            elif SYMBOL.fullmatch(token):
                if token not in symbols:
                    if next_ram >= PREDEFINED["SCREEN"]:
                        raise ValueError("variable RAM exhausted")
                    symbols[token] = next_ram
                    next_ram += 1
                value = symbols[token]
            else:
                raise ValueError(f"invalid A-instruction {command!r}")
            if not 0 <= value <= 32767:
                raise ValueError("A-instruction value must be 0 to 32767")
            words.append(f"{value:016b}")
        except ValueError as error:
            raise ValueError(f"Line {number}: {error}") from None
    return words


def main():
    parser = argparse.ArgumentParser(description="Assemble a Hack program")
    parser.add_argument("source", type=Path, help="input .asm file")
    args = parser.parse_args()
    if args.source.suffix.lower() != ".asm":
        parser.error("expected an .asm input file")
    try:
        words = assemble(args.source.read_text(encoding="utf-8"))
        output = args.source.with_suffix(".hack")
        output.write_text("".join(word + "\n" for word in words),
                          encoding="ascii")
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"{output.name}: {len(words)} instructions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
