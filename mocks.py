class DokuToken:
    def __init__(self):
        self.balances = dict()
    
    def transfer(self, _from, _to, _amount):
        self.balances[_from] -= _amount
        self.balances[_to] += _amount

    def mint(self, _to, _amount):
        self.balances[_to] += _amount

    def balanceOf(self, _of):
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
            if all(val['tokens'] == tokens) and all(val['weights'] == weights):
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
        return pid


    def addLiquidity(self, user, pid, tokens, amounts):
        self.pools[pid]['users'][user].setdefault('amounts', {})

        for token, amount in zip(tokens, amounts):
            self.pools[pid]['amounts'][token] += amount
            self.pools[pid]['users'][user]['amounts'].setdefault(token, 0)
            self.pools[pid]['users'][user]['amounts'][token] += amount

    
    def removeLiquidity(self, user, pid, tokens, amounts):
        for token, amount in zip(tokens, amounts):
            self.pools[pid]['amounts'][token] -= amount
            self.pools[pid]['users'][user]['amounts'][token] -= amount

    
        





