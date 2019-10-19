import os

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in sorted(files):
    # print(f)
    if f != os.path.basename(__file__) and f.endswith("py"):
        print('Executing {0}'.format(f))
        c = input("Continue? y/n")
        if c == "n" or c == "no":
            break
        os.system("../build/manta {0}".format(f))
