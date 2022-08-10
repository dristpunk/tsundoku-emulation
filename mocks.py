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

    def balanceOf(self, _of):
        self.balances.setdefault(_of, 0)
        return self.balances[_of]


class Treasury:
    def __init__(self):
        self.balance = dict()

    def _addTokens(self, tokens, amounts):
        self.balance = dict(dict.items() + zip(tokens, amounts))


class Router:
    def __init__(self, farms):
        self.pools = []
        self.farms = farms


    def _getPoolId(self, tokens, weights):
        for pid, val in enumerate(self.pools):
            if (val['amounts'].keys() == tokens) and (val['weights'].values() == weights):
                return pid

        return -1


    def createPool(self, user, tokens, weights, amounts):
        pid = self._getPoolId(tokens, weights)
        if pid != -1:
            raise Exception("Pool already exists")

        pool = {
            'amounts': dict(zip(tokens, amounts)),
            'weights': dict(zip(tokens, weights)),
            'users': {user: {
                'amounts': dict(zip(tokens, amounts))
            }}
        }

        self.pools.append(pool)
        return len(self.pools) - 1


    def addLiquidity(self, user, pid, tokens, amounts):
        self.pools[pid]['users'].setdefault(user, {'amounts': {}})

        for token, amount in zip(tokens, amounts):
            self.pools[pid]['amounts'][token] += amount
            self.pools[pid]['users'][user]['amounts'].setdefault(token, 0)
            self.pools[pid]['users'][user]['amounts'][token] += amount

    
    def removeLiquidity(self, user, pid, tokens, amounts):
        for token, amount in zip(tokens, amounts):
            self.pools[pid]['amounts'][token] -= amount
            self.pools[pid]['users'][user]['amounts'][token] -= amount

    
        





