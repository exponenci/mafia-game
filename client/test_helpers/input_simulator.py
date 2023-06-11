import random

def simulate_input_session(vote_options: str):
    if random.choice([True, False]):
        return {
            'message': random.choice([ # some random words as messages from users
                'test message: obsequious',
                'test message: glossy',
                'test message: different',
                'test message: argue',
                'test message: shrill',
                'test message: picayune',
                'test message: ants',
                'test message: wrathful',
                'test message: arch',
                'test message: lamentable',
                'test message: boil',
                'test message: practice', 
                'test message: task', 
                'test message: message'
            ])
        }
        # generate chat message...
        pass
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
