from re import L
from mocks import ERC20


class User:
    def __init__(self, name, farms):
        self.name = name
        self.farms = farms
        self.assets = {}
    
    def mintTokens(self, assets, amounts):
        if isinstance(assets, list) and isinstance(amounts, list):
            assert(len(assets) == len(amounts))
            for asset, amount in zip(assets, amounts):
                asset.mint(self, amount)
                self.assets[asset.name] = amount

        elif isinstance(asset, ERC20) and isinstance(amounts, int):
            asset.mint(self, amounts)
            self.assets[asset.name] = amount

        else:
            assert(False)


    def createPool(self, tokens, weights, amounts):
        self.farms.createPool(self, tokens, weights, amounts)
        for token, amount in zip(tokens, amounts):
            self.assets[token.name] -= amount

    def deposit(self, pid, tokens, amounts):
        self.farms.deposit(self, pid, tokens, amounts)
        for token, amount in zip(tokens, amounts):
            self.assets[token.name] -= amount

    def harvest(self, pids):
        if isinstance(pids, list):
            self.farms.harvestAll(self, pids)
        
        elif isinstance(pids, int):
            self.farms.harvest(self, pids)

        else:
            assert(False)

    def withdraw(self, pids):
        if isinstance(pids, list):
            for pid in pids:
                tokens = list(self.farms.userInfo[pid][self]['amounts'].keys())
                amounts = list(self.farms.userInfo[pid][self]['amounts'].values())
                self.farms.withdrawAndHarvest(self, pid, tokens, amounts)

        elif isinstance(pids, int):
            tokens = list(self.farms.userInfo[pids][self]['amounts'].keys())
            amounts = list(self.farms.userInfo[pids][self]['amounts'].values())
            self.farms.withdrawAndHarvest(self, pids, tokens, amounts)
