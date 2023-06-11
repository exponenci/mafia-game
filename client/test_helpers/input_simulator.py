import random

def simulate_input_session(vote_options: str):
    session_cmds = [
        '!help', 
        '!tab', 
        '!status', 
        '!pick', 
        '!skip', 
    ]
    cmd = random.choice(session_cmds)
    if cmd == '!pick':
        arg = random.choice(vote_options)
        return {'cmd': cmd, 'arg': arg}
    return {'cmd': cmd}

def simulate_input_core():
    return '!exit'
    # if you enable !new option for core-input
    # make sure, that eventually client will be able to find
    # someone to play with or exit
    core_cmds = ['!new', '!exit']
    cmd = random.choice(core_cmds)
    return {'cmd': cmd}
