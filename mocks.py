class ERC20:
    def __init__(self, name):
        self.balances = dict()
        self.name = name
    
    def transfer(self, _from, _to, _amount):
        assert self.balances[_from] >= _amount

        self.balances.setdefault(_to, 0)
        self.balances[_from] -= _amount
        self.balances[_to] += _amount

    def mint(self, _to, _amount):
        self.balances.setdefault(_to, 0)
        self.balances[_to] += _amount

    def burn(self, _from, _amount):
        assert self.balance[_from] >= _amount
        self.balance[_from] -= _amount

    def balanceOf(self, _of):
        self.balances.setdefault(_of, 0)
        return self.balances[_of]

    def __lt__(self, other):
         return self.name < other.name



class Treasury:
    def __init__(self):
        self.balance = dict()
        self.name = 'TREASURY'

    def _addTokens(self, tokens, amounts):
        for token, amount in zip(tokens, amounts):
            self.balance.setdefault(token, 0)
            self.balance[token] += amount

    def getBalance(self):
        view_dict = {}
        for token in self.balance:
            view_dict[token.name] = self.balance[token]

        return view_dict


class Router:
    def __init__(self, farms, prices):
        self.pools = []
        self.farms = farms
        self.prices = prices
        self.name = 'ROUTER'


    def _getPoolId(self, tokens, weights):
        for pid, val in enumerate(self.pools):
            if (val['amounts'].keys() == tokens) and (val['weights'].values() == weights):
                return pid

        return -1

    def getPools(self):
        res_list = []
        for pool in self.pools:
            view_pool = {
            'amounts': {tok.name:val for tok, val in pool['amounts'].items()},
            'weights': {tok.name:val for tok, val in pool['weights'].items()},
            'users': {usr.name: lp for usr, lp in pool['users'].items()}
            }

            res_list.append(view_pool)

        return res_list


    def rebaseAmounts(self, tokens, amounts, weights):
        sumPrice = sum([self.prices[tok] * amt for tok, amt in zip(tokens, amounts)])
        new_amounts = [w * sumPrice for w in weights.values()]

        for token, amt, newAmt in zip(tokens, amounts, new_amounts):
            token.burn(self, amt)
            token.mint(self, newAmt)

        return new_amounts
        

    def createPool(self, user, tokens, weights, amounts):
        pid = self._getPoolId(tokens, weights)
        if pid != -1:
            raise Exception("Pool already exists")
        
        new_amounts = self.rebaseAmounts(tokens, amounts, weights) # instant arbitrage

        pool = {
            'amounts': dict(zip(tokens, new_amounts)),
            'weights': dict(zip(tokens, weights)),
            'users': {user: 1} # 1 LP for first dude
        }

        self.pools.append(pool)
        return len(self.pools) - 1


    def addLiquidity(self, user, pid, tokens, amounts):
        self.pools[pid]['users'].setdefault(user, 0)

        new_amounts = self.rebaseAmounts(tokens, amounts, self.pools[pid]['weights']) # instant arbitrage
        
        self.pools[pid]['users'][user] += new_amounts[0] / self.pools[pid]['amounts'][tokens[0]] # LP

        for token, amount in zip(tokens, new_amounts):
            self.pools[pid]['amounts'][token] += amount
        

    
    def removeLiquidity(self, user, pid, lps):
        assert lps <= self.pools[pid]['users'][user]

        pool = self.pools[pid]

        lpall = sum(pool['users'].values())

        for token, amount in pool['amounts'].items():
            toReturn = lps / lpall * amount

            pool['amounts'][token] -= toReturn

            token.transfer(self.router, user, toReturn)

        pool['users'][user] -= lps


    def changeTokenPrice(self, token, new_price):
        assert new_price > 0

        n = new_price / self.prices[token] 

        for pool in self.pools:
            if token not in pool['amounts']:
                continue
            
            new_amounts = []
            a = pool['weights'][tok]
            for tok in pool['amounts']:
                val = pool['amounts'][tok]
                new_val = val * n**(a - (tok == token)) # good formula uwu
                new_amounts.append((tok, new_val))

            pool['amounts'] = dict(new_amounts)

        self.prices[token] = new_price
            
        





