# import os
# import sys
# import inspect

# currentdir = os.path.dirname(
#     os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)

from subprocess import Popen, PIPE, STDOUT
import random
import string


def generate_string(n: int = 5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


def run_client():
    username_variants = [generate_string() for _ in range(5)]
    p_input = '\n'.join(username_variants)
    p = Popen("python3 main.py", 
              stdout=PIPE, 
              stdin=PIPE, 
              stderr=STDOUT, 
              shell=True)
    out = p.communicate(input=p_input.encode())[0]
    with open(f'outs/core/{username_variants[0]}', 'wb') as f:
        f.write(out)

if __name__ == '__main__':
    run_client()
