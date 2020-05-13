import difflib
import sys
from colorama import Fore, Back, Style


def print_diff(s1, s2):
    # s1, s2 = sys.argv[1:2]

    s = difflib.SequenceMatcher(None, s1, s2)

    original_colors = {
        "delete": Fore.BLACK + Back.RED,
        "equal": "",
        "insert": "",
        "replace": Fore.BLACK + Back.YELLOW,
    }
    new_colors = {
        "delete": "",
        "equal": "",
        "insert": Fore.BLACK + Back.GREEN,
        "replace": Fore.BLACK + Back.YELLOW,
    }
    old_seq = []
    new_seq = []

    for tag, i1, i2, j1, j2 in s.get_opcodes():
        old_length = i2 - i1
        new_length = j2 - j1
        length_diff = new_length - old_length
        for c in s1[i1:i2]:
            old_seq.append((original_colors[tag], c))
        for c in s2[j1:j2]:
            new_seq.append((new_colors[tag], c))
        if length_diff > 0:
            old_seq += [("", None)] * length_diff

        elif length_diff < 0:
            new_seq += [("", None)] * (-length_diff)

    width = 16
    weave_seq(old_seq, new_seq, width)


def weave_seq(seq1, seq2, width):
    for i, index in enumerate(range(0, max(len(seq1), len(seq2)), width)):
        for seq in (seq1, seq2):
            line_toks = seq[index : index + width]
            line = get_line(line_toks)
            print(f"{hex(index).rjust(5)}: {line}")


def print_seq(seq, width):
    for index in range(0, len(seq), width):
        line_toks = seq[index : index + width]
        line = get_line(line_toks)
        print(line)

def get_line(line_toks):
    chars = []
    for tok in line_toks:
        if tok[1] != None:
            try:
                chars.append(tok[0] + hex(tok[1])[2:].rjust(2, "0") + Style.RESET_ALL)
            except:
                print(line_toks)
        else:
            chars.append("  ")
    return "".join(chars)

print("Reloaded!")
