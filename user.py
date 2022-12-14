from re import L
from mocks import ERC20


class User:
    def __init__(self, name, farms, router):
        self.name = name
        self.farms = farms
        self.router = router
        self.assets = {}
    
    def mintTokens(self, assets, amounts):
        if isinstance(assets, list) and isinstance(amounts, list):
            assert(len(assets) == len(amounts))
            for asset, amount in zip(assets, amounts):
                asset.mint(self, amount)
                self.assets[asset] = amount

        elif isinstance(assets, ERC20) and isinstance(amounts, int):
            assets.mint(self, amounts)
            self.assets[assets] = amounts

        else:
            assert(False)


    def createPool(self, tokens, weights, amounts):
        self.farms.createPool(self, tokens, weights, amounts)
        for token, amount in zip(tokens, amounts):
            self.assets[token] -= amount

    def deposit(self, pid, tokens, amounts):
        self.farms.deposit(self, pid, tokens, amounts)
        for token, amount in zip(tokens, amounts):
            self.assets[token] -= amount

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
                lps = self.router.pools[pid]['users'][self]
                return_tokens, return_amounts = self.farms.withdrawAndHarvest(self, pid, lps)
                for tok, amt in zip(return_tokens, return_amounts):
                    self.assets.setdefault(tok, 0)
                    self.assets[tok] += amt

        elif isinstance(pids, int):
            lps = self.router.pools[pids]['users'][self]
            return_tokens, return_amounts = self.farms.withdrawAndHarvest(self, pids, lps)
            for tok, amt in zip(return_tokens, return_amounts):
                    self.assets.setdefault(tok, 0)
                    self.assets[tok] += amt

    def getAssets(self):
        return {tok.name: amt for tok, amt in self.assets.items()}
