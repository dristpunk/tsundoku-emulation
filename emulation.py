from farms import Farms
from mocks import Router, Treasury, ERC20
from user import User
from time import time


class Emulation:
    def __init__(self):
        self.farms = Farms(10e18, 100) # 10 doku per block and 10% treasury percent
        self.treasury = Treasury()
        self.doku = ERC20('doku')

        tokens_names = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.tokens = [ERC20(name) for name in tokens_names]
        price_list = sorted(list(range(1, 14, 1)) * 2, reverse=True) # [13, 13, 12, 12, ..., 1, 1]
        prices = {token: price for token, price in zip(self.tokens, price_list)}

        self.router = Router(self.farms, prices)

        users_names= ['alice', 'bob', 'carol', 'david', 
             'eva', 'finn', 'gleb', 'harry', 
             'ivan', 'jack', 'kevin', 'larry', 
             'mary', 'nick', 'oliver', 'peter', 
             'quill', 'rug', 'steve', 'tarry', 
             'ulia', 'vasy', 'will', 'xavier', 
             'yair', 'zoe']
        self.users = [User(name, self.farms, self.router) for name in users_names]

        self.farms.initialize(self.doku, self.treasury, self.router)

        self.host = User('HOST', self.farms, self.router)

        for token, point in zip(self.tokens, price_list): # weights same with prices
            self.farms.setToken(token, point)

        for user in self.users:
            user.mintTokens(self.tokens, [1000] * len(self.tokens))

        # initial pools to display
        self.farms.createPool(self.users[0], self.tokens[:2], [0.5, 0.5], [100, 100])
        self.farms.createPool(self.users[1], self.tokens[1:3], [0.5, 0.5], [100, 100])
        self.farms.createPool(self.users[2], self.tokens[2:4], [0.5, 0.5], [100, 100])
        self.farms.createPool(self.users[3], self.tokens[:4], [0.25, 0.25, 0.25, 0.25], [100, 100, 100, 100])

        self.start_time = time()
        self.time_stopped = self.start_time

    def start(self):
        self.time_stopped = None

    def getBlock(self):
        if self.time_stopped is None:
            return int(time() - self.start_time)
        
        return int(self.time_stopped - self.start_time)

    def addBlocks(self, n):
        self.start_time -= n

    def subBlocks(self, n):
        self.start_time += n

    def stop(self):
        self.time_stopped = time()

    def logState(self):
        logs = {
            'pools': self.router.getPools(),
            'users': self.farms.getUsers(),
            'tokens': {tok: info for tok, info in self.farms.getTokens().items() if info['accDokuPerShare'] != 0},
            'treasury': self.treasury.getBalance()
        }
        return logs

    

    
