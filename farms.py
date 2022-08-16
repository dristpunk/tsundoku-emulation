from copy import copy, deepcopy


def arrayIsSorted(arr):
        if not (arr == sorted(arr)) and (len(set(arr)) == len(arr)):
            print([a.name for a in arr])
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
        self.name = 'FARMS'

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
        assert amount - self.doku.balanceOf(self) <= 1e18

        self.doku.transfer(self, to, min(amount, self.doku.balanceOf(self)))

    
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

        for token_, amount_ in zip(tokens, amounts):
            token_.transfer(sender, self.router, amount_)

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

    def updateToken(self, _token):
        token = self.tokenInfo[_token]

        if self.block > token['lastRewardBlock']:
            if token['amount'] > 0:
                blocksSinceLastReward = self.block - token['lastRewardBlock']
                dokuRewards = (blocksSinceLastReward * self.dokuPerBlock * token['allocPoint']) // self.totalAllocPoint
                self.doku.mint(self, dokuRewards)
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

            token_.transfer(sender, self.router, amount_)

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
    

    def withdrawAndHarvest(self, sender, pid, lps):
        userLps = self.router.pools[pid]['users'][sender]
        assert lps <= userLps

        user = self.userInfo[pid][sender]

        accumulatedDoku = 0
        rewardDebtDecay = 0

        return_tokens, return_amounts = self.router.removeLiquidity(sender, pid, lps)

        share = lps / userLps

        for token_ in user['amounts'].keys():
            
            amount_ = user['amounts'][token_] * share

            self.updateToken(token_)

            token = self.tokenInfo[token_]

            accumulatedDoku += (user['amounts'][token_] * token['accDokuPerShare'])  // self.ACCOUNT_PRECISION

            rewardDebtDecay += (amount_ * token['accDokuPerShare']) // self.ACCOUNT_PRECISION

            user['amounts'][token_] -= amount_
            token['amount'] -= amount_ 

        eligibleDoku = accumulatedDoku - user['rewardDebt']

        user['rewardDebt'] = accumulatedDoku - rewardDebtDecay

        self.safeDokuTransfer(sender, eligibleDoku)

        return return_tokens, return_amounts
        
    def updateEmissionRate(self, newRate):
        self.dokuPerBlock = newRate

    def getUsers(self):
        user_info = {pool: {user.name: {'amounts': {tok.name:amt for tok, amt in uinf['amounts'].items()}, 'rewardDebt': uinf['rewardDebt']} for user, uinf in pinf.items()}  for pool, pinf in self.userInfo.items()}

        return user_info

    def getTokens(self):
        token_info = {tok.name: deepcopy(inf) for tok, inf in self.tokenInfo.items()}
        return token_info

