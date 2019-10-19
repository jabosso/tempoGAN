import os

index = 4
files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith("py")]
files = sorted(files)
print(files[index])
params = {}
params['--ball-height'] = '0.8'
params['--ball-radius'] = '0.1'
params['--ball-speed'] = '5'
params['--res'] = '64'
params['--pause-starting'] = ''

all_params = ""
for key in params:
    all_params += " {0} {1}".format(key, params[key])

os.system("../build/manta {0} {1}".format(files[index], all_params))
