allText = {}
lineNum = None
with open("possibleMoves - Copy.c") as f:
    for line in f:
        if line.startswith("  /* \"possibleMoves.py\""):
            lineNum = int(line.partition("\"possibleMoves.py\":")[2].strip())
        elif line.startswith(" *") and not line.startswith(" */"):
            if lineNum != None:
                lineNum += 1
                if lineNum not in allText:
                    allText[lineNum] = line.strip()[2:].rstrip("             # <<<<<<<<<<<<<<")
        else:
            lineNum = None

i = 0
while True:
    if i in allText:
        print(allText[i])
    else:
        print()
    i += 1

"""There are still spaces of blank text"""
