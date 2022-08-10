from copy import copy, deepcopy


def arrayIsSorted(arr):
        return (arr == sorted(arr)) and (len(set(arr)) == len(arr))


class Farms:
    def __init__(self, dokuPerBlock, treasuryPercent):
        self.dokuPerBlock = dokuPerBlock
        self.treasuryPercent = treasuryPercent
        self.tokenInfo = {}
        self.userInfo = {}
        self.block = 0
        self.totalAllocPoint = 0
        self.ACCOUNT_PRECISION = 1e12

    def initialize(self, doku, treasury, router):
        self.doku = doku
        self.treasury = treasury
        self.router = router

    def getTokenInfo(self):
        res_dict = {}
        for token in self.tokenInfo:
            res_dict[token.name] = deepcopy(self.tokenInfo[token])

        return res_dict
    
    def getUserInfo(self):
        res_dict = {}
        for pool in self.userInfo:
            res_dict[pool] = {}
            for user in pool:
                res_dict[pool][user.name] = deepcopy(self.userInfo[pool][user])

        return res_dict


    def safeDokuTransfer(self, to, amount):
        self.doku.transfer('farms', to, min(amount, self.doku.balanceOf('farms')))

    
    def setToken(self, token, allocPoint):
        self.tokenInfo.setdefault(token, {"allocPoint": 0,
                                        "lastRewardBlock": 0,
                                        "accDokuPerShare": 0,
                                        "amount": 0})

        self.totalAllocPoint = self.totalAllocPoint - self.tokenInfo[token]['allocPoint'] + allocPoint
        self.tokenInfo[token]['allocPoint'] = allocPoint

    
    def createPool(self, sender, tokens, weights, amounts):
        assert len(tokens) == len(weights) == len(amounts)
        assert arrayIsSorted(tokens)

        pid = self.router.createPool(sender, tokens, weights, amounts)
        assert(pid not in self.userInfo)

        self.userInfo.setdefault(pid, {})

        self.userInfo[pid][sender] = {'amounts': {}, 'rewardDebt': 0}
        
        user = self.userInfo[pid][sender]

        for token_, amount_ in zip(tokens, amounts):
            
            self.updateToken(token_)

            token = self.tokenInfo[token_]

            user['rewardDebt'] += (amount_ * token['accDokuPerShare']) // self.ACCOUNT_PRECISION
            user['amounts'][token_] = amount_
            
            token['amount'] += amount_

            token_.transfer(sender, self.router, amount_)

    def updateToken(self, _token):
        token = self.tokenInfo[_token]

        if self.block > token['lastRewardBlock']:
            if token['amount'] > 0:
                blocksSinceLastReward = self.block - token['lastRewardBlock']
                dokuRewards = (blocksSinceLastReward * self.dokuPerBlock * token['allocPoint']) // self.totalAllocPoint
                self.doku.mint('farms', dokuRewards)
                treasuryRewards = (dokuRewards * self.treasuryPercent) // 1000
                self.doku.mint(self.treasury, treasuryRewards)
                token['accDokuPerShare'] += (dokuRewards * self.ACCOUNT_PRECISION) // token['amount']

            token['lastRewardBlock'] = self.block


    def massUpdateTokens(self):
        for token in self.tokenInfo:
            self.updateToken(token)


    def deposit(self, sender, pid, tokens, amounts):
        assert(len(tokens) == len(amounts))
        assert(arrayIsSorted(tokens))

        self.userInfo[pid].setdefault(sender, {'amounts': {}, 'rewardDebt': 0})
        
        user = self.userInfo[pid][sender]

        for token_, amount_ in zip(tokens, amounts):
            
            self.updateToken(token_)

            token = self.tokenInfo[token_]

            user['rewardDebt'] += (amount_ * token['accDokuPerShare']) // self.ACCOUNT_PRECISION

            user['amounts'].setdefault(token_, 0)
            user['amounts'][token_] += amount_
            
            token['amount'] += amount_

        self.router.addLiquidity(sender, pid, tokens, amounts)


    def harvest(self, sender, pid):
        user = self.userInfo[pid][sender]

        accumulatedDoku = 0

        for token_, amount_ in user['amounts'].items():
            self.updateToken(token_)
            token = self.tokenInfo[token_]
            accumulatedDoku += amount_ * token['accDokuPerShare']

        eligibleDoku = (accumulatedDoku // self.ACCOUNT_PRECISION) - user['rewardDebt']

        user['rewardDebt'] = accumulatedDoku

        if eligibleDoku > 0:
            self.safeDokuTransfer(sender, eligibleDoku)


    def harvestAll(self, sender, pids):
        for pid in pids:
            self.harvers(sender, pid)
    

    def withdrawAndHarvest(self, sender, pid, tokens, amounts):
        user = self.userInfo[pid][sender]
        assert(len(tokens) == len(amounts))
        assert(arrayIsSorted(tokens))

        accumulatedBeets = 0
        rewardDebtDecay = 0

        self.router.removeLiquidity(sender, pid, tokens, amounts)

        for token_, amount_ in zip(tokens, amounts):

            assert(amount_ <= user['amounts'][token_])

            self.updateToken(token_)

            token = self.tokenInfo[token_]

            accumulatedBeets += user['amounts'][token_] * token['accDokuPerShare']

            rewardDebtDecay += amount_ * token['accDokuPerShare']

            user['amounts'][token_] -= amount_
            token['amount'] -= amount_

            token_.transfer(self.router, sender, amount_)

        eligibleBeets = (accumulatedBeets // self.ACCOUNT_PRECISION) - user['rewardDebt']

        user['rewardDebt'] = accumulatedBeets - (rewardDebtDecay // self.ACCOUNT_PRECISION)

        self.safeDokuTransfer(sender, eligibleBeets)
        
    def updateEmissionRate(self, newRate):
        self.dokuPerBlock = newRate

