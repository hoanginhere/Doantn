
text = input()

heart = [
    "  **   **  ",
    " **** **** ",
    "********** ",
    "**********",
    " ********* ",
    "  *******  ",
    "   *****   ",
    "    ***    ",
    "     *     "
]

for line in heart:
    print(line.replace("*", text))