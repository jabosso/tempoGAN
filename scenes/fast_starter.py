import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num", type=int, default=7,
                    help="Number of env (default: 7)")
parser.add_argument("--list", action="store_true", default=False,
                    help="Show list of fast starting envs")
args = parser.parse_args()
experiment_number = args.num

if args.list:
    print('1: flip02_surface')
    print('2: turbulence')
    print('3: apic01_simple')
    print('4: fire')
    print('5: flip02_chair')
    print('6: guiding_2d')
    print('7: newscene')
    experiment_number = -1

start_all_defaults = False


def start(params, executable):
    all_params = ""
    for key in params:
        all_params += " {0} {1}".format(key, params[key])
    os.system("../build/manta {0} {1}".format(executable, all_params))


if start_all_defaults:
    index = 4
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith("py")]
    files = sorted(files)
    executable = files[index]

# Number 1
if experiment_number == 1:
    executable = "flip02_surface.py"
    print(executable)
    params = {}
    params['--ball-radius'] = .1
    params['--ball-speed'] = .3
    params['--res'] = '64'
    params['--pause-starting'] = ''

    start(params, executable)

# Number 2
if experiment_number == 2:
    executable = "turbulence.py"
    print(executable)
    params = {}
    params['--speed-x'] = 0.8
    params['--speed-y'] = 0.1
    params['--speed-z'] = 0.0
    params['--turb-number'] = 1000
    params['--pause-starting'] = ''
    params['--res'] = 64
    params['--save-parts'] = ''

    params['--scene'] = 4

    startr_all = True
    if startr_all:
        for i in range(4):
            params['--scene'] = i
            start(params, executable)
    else:
        start(params, executable)

# Number 3
if experiment_number == 3:
    executable = "apic01_simple.py"
    print(executable)
    params = {}
    params['--gravity-x'] = 0.001
    params['--gravity-y'] = 0.003
    params['--gravity-z'] = 0.0
    params['--box-altitude-top'] = 0.9
    params['--box-height'] = .3
    params['--box-width'] = .3
    params['--res'] = '64'
    params['--particle-number'] = 15
    params['--pause-starting'] = ''
    params['--save-parts'] = ''
    params['--save-each'] = 15

    start(params, executable)

# Number 4
if experiment_number == 4:
    executable = "fire.py"
    print(executable)
    params = {}
    params['--gravity-x'] = 0.0
    params['--gravity-y'] = 0.008
    params['--gravity-z'] = 0.0
    params['--box-height'] = .92
    params['--box-dim'] = .3
    params['--res'] = '64'
    params['--particle-number'] = 10
    params['--pause-starting'] = ''

    start(params, executable)

# Number 5 Chair
if experiment_number == 5:
    executable = "flip02_chair.py"
    print(executable)
    params = {}
    params['--ball-radius'] = .1
    params['--ball-speed'] = .3
    params['--res'] = '64'
    params['--pause-starting'] = ''
    params['--partic-rad'] = 0.9

    start(params, executable)

# Number 6 Another test
if experiment_number == 6:
    executable = "guiding_2d.py"
    print(executable)
    params = {}
    start(params, executable)

# Number 6 Another test
if experiment_number == 7:
    executable = "newscene.py"
    print(executable)
    params = {}
    start(params, executable)
