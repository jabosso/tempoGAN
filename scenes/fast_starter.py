import os

experiment_number = 2

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
    params['--ball-height'] = '0.8'
    params['--ball-radius'] = '0.1'
    params['--ball-speed'] = '5'
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
    params['--turb-number'] = 2000
    params['--pause-starting'] = ''
    params['--res'] = 128

    for i in range(4):
        params['--scene'] = i
        start(params, executable)
