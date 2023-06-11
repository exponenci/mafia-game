import random
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class VotePool:
    votes_count: int = 0
    expect_votes_count: int = 0
    expect_votes: Dict[str, bool] = field(default_factory=dict) # username - is_voted
    target_votes: Dict[str, int] = field(default_factory=dict) # target - how many votes

    def reset(self, voters_list: List[str], options_list: List[str]):
        self.votes_count = 0
        self.expect_votes_count = len(voters_list)
        self.expect_votes = dict(zip(
            voters_list, 
            [False for _ in range(len(voters_list))]
        ))
        random.shuffle(options_list)
        self.target_votes = dict(zip(
            options_list, 
            [0 for _ in range(len(options_list))]
        ))

    def accept_vote(self, username: str, target: str):
        if username in self.expect_votes and \
                not self.expect_votes[username]:
            if target in self.target_votes:
                self.expect_votes[username] = True
                self.target_votes[target] += 1
                self.votes_count += 1
                return True
            if target == '' and \
                    (self.votes_count + 1 < self.expect_votes_count or 
                     self.is_valid()):
                self.expect_votes[username] = True
                self.votes_count += 1
                return True
        return False
    
    def is_full(self) -> bool:
        return self.votes_count == self.expect_votes_count

    def is_valid(self) -> bool:
        if self.expect_votes_count == 1 and self.is_full():
            return True
        votes = sorted(list(self.target_votes.values()))
        return votes[-1] != votes[-2]

    def get_poll_result(self) -> str: # username
        return sorted(
            list(self.target_votes.items()), 
            key=lambda item: item[1]
        )[-1][0]
