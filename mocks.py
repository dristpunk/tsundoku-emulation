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

    def __lt__(self, other):
         return self.name < other.name



class Treasury:
    def __init__(self):
        self.balance = dict()

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
    def __init__(self, farms):
        self.pools = []
        self.farms = farms


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
            'users': {user.name:{'amounts': {t.name:v for t,v in val['amounts'].items()}} for user, val in pool['users'].items()}
            }

            res_list.append(view_pool)

        return res_list

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


    def changeTokenPrice(self, token, n):
        for pool in self.pools:
            if token not in pool['amounts']:
                continue
            
            new_amounts = []
            a = pool['weights'][tok]
            for tok in pool['amounts']:
                val = pool['amounts'][tok]
                if tok == token:
                    new_val = val /  (n**(1 - a))
                else:
                    new_val = val * n /  (n**(1 - a))
                    
                new_amounts.append(new_val)
        





