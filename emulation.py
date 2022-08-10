from farms import Farms
from mocks import Router, Treasury, ERC20
from user import User


class Emulation:
    def __init__(self):
        self.farms = Farms(10e18, 100) # 10 doku per block and 10% treasury percent
        self.router = Router(self.farms)
        self.treasury = Treasury()
        self.doku = ERC20('doku')

        users_names= ['alice', 'bob', 'carol', 'david', 
             'eva', 'finn', 'gleb', 'harry', 
             'ivan', 'jack', 'kevin', 'larry', 
             'mary', 'nick', 'oliver', 'peter', 
             'quill', 'rug', 'steve', 'tarry', 
             'ulia', 'vasy', 'will', 'xavier', 
             'yair', 'zoe']
        self.users = [User(name, self.farms) for name in users_names]

        tokens_names = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.tokens = [ERC20(name) for name in tokens_names]

        self.host = User('host', self.farms)

        point_list = sorted(list(range(100,1400, 100)) * 2, reverse=True) # [1300, 1300, 1200, 1200, ..., 100, 100]
        for token, point in zip(self.tokens, point_list):
            self.farms.setToken(token, point)

        for user in self.users:
            user.mintTokens(self.tokens, [1000] * len(self.tokens))

        self.farms.createPool(self.users[0], self.tokens[:2], [50,50], [100, 100])
        self.farms.createPool(self.users[1], self.tokens[1:3], [50,50], [100, 100])
        self.farms.createPool(self.users[2], self.tokens[2:4], [50,50], [100, 100])
        self.farms.createPool(self.users[3], self.tokens[:4], [25,25,25,25], [100, 100, 100, 100])