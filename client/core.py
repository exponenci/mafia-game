import os
import asyncio
from typing import Iterable, List, Optional, Tuple, Dict
from dataclasses import dataclass, field

from test_helpers.input_simulator import simulate_input_core, simulate_input_session


@dataclass
class ClientCore:
    # session info for client
    username: str = ''
    session_id: str = ''
    role: str = ''
    alive: bool = True
    voted: bool = False
    session_players: List[str] = field(default_factory=list) # username
    killed_players: List[Tuple[str, str]] = field(default_factory=list) # username, role

    # turn info
    turn: str = ''
    prev_turn: str = ''
    target: Optional[Tuple[str, str]] = None # username, role
    vote_options: Optional[List[str]] = None # usernames

    HELP_CMD_RESPONSE_MSG = """\n Session commands:
       !tab            shows session info
       !status         shows your role and status
       !pick <name>    vote for/pick <name> for poll
       !skip           skip vote
       !clear          clears terminal
    \n Core commands (runs only after the session is over):
       !new            stay in queue to new session
       !exit           exit
    """

    def print(self, line, prefix: str = ''):
        if prefix == '':
            if self.session_id == '':
                prefix = 'core'
            else:
                prefix = 'session'
        print(f'${prefix}> ' + line, flush=True)

    def print_session_info(self):
        self.print(f'You are connected to session#{self.session_id}')
        self.print(f'Your role: {self.role}')
        self.print(f'Players in session:')
        for player_username in self.session_players:
            self.print(f'- {player_username}')

    def print_turn_info(self):
        if self.target is not None and self.target[0] != '':
            if self.prev_turn == 'Citizens':
                self.print(f'{self.target[0]} was hanged by citizens! He was {self.target[1]}...')
                self.print(f'The night is coming...')
            elif self.prev_turn == 'Mafia':
                self.print(f'{self.target[0]} was killed! He was {self.target[1]}...')
            elif self.prev_turn == 'Commissar':
                self.print(f'The player who was checked by commissar is {self.target[1]}!')
            if self.turn == 'Citizen':
                self.print(f'Good morning everyone!')
        self.print(f'{self.turn}\'s turn...')
        if self.alive and self.vote_options is not None and \
                len(self.vote_options) != 0 and \
                (self.turn == self.role or self.turn == 'Citizen'):
            self.print(f'pick someone from options below')
            for option in self.vote_options:
                self.print(f'- {option}')

    def print_result(self, citizens_wins: bool, data: dict):
        self.print(f"===  GAME OVER!   ===")
        if citizens_wins:
            self.print(f"=== CITIZENS WIN! ===")
        else:
            self.print(f"===  MAFIA WINS!  ===")
        for username, info in data.items():
            status = 'alive' if info[0] else 'dead'
            self.print(f"- {username} is {status} [{info[1]}]")
    
    def reset(self):
        self.session_id = ''
        self.role = ''
        self.alive = True
        self.voted = False
        self.turn = ''
        self.prev_turn = ''
        self.target = None
        self.vote_options = None

    def set_session_info(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def set_turn_info(self, **kwargs):
        self.prev_turn = self.turn
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if self.target is not None and self.target[0] == self.username:
            self.alive = False
        self.voted = False

    async def run(self) -> Iterable[Dict[str, str]]:
        print("RUN")
        while self.session_id != '':
            # print("TURN", self.turn)
            if not self.voted and self.alive and (self.turn == self.role or self.turn == 'Citizen'):
                data = simulate_input_session(self.vote_options)
                # self.print('!pick')
                print("YOUR DATA:", data, self.username)
                if 'arg' in data:
                    self.print(data['cmd'] + data['arg'])
                else:
                    self.print(data['cmd'])
                if data['cmd'].startswith('!'):
                    if data['cmd'] == '!help':
                        self.print(self.HELP_CMD_RESPONSE_MSG)
                    elif data['cmd'] == '!tab':
                        self.print('Players:')
                        killed = dict(self.killed_players)
                        for username in self.session_players:
                            if username in killed:
                                self.print(f' - {username} is killed [{killed[username]}]')
                            else:
                                self.print(f' - {username} is alive')
                    elif data['cmd'] == '!status':
                        self.print(f'Role: {self.role}. Status: alive')
                    elif data['cmd'] == '!pick':
                        if data['arg'] != self.username and data['arg'] in self.vote_options:
                            self.voted = True
                            yield data
                        else:
                            self.print('Invalid !pick param... Pick from given options and not yourself')
                    elif data['cmd'] == ['!skip']:
                        self.voted = True
                        yield {'cmd': '!pick', 'arg': ''}
                    elif data['cmd'] == '!clear':
                        os.system('clear')
            if self.turn == 'over':
                data = simulate_input_core()
                self.print(data, self.username)
                if data == '!new':
                    self.reset()
                    yield {'cmd': data}
                    break
                elif data == '!exit':
                    yield {'cmd': data}
                    break
            await asyncio.sleep(1)
