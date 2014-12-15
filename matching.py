from bisect import bisect_right
from bisect import bisect_left


class Side():
    Buy, Sell = range(2)

    @staticmethod
    def opposite_of(side):
        return Side.Buy if side is Side.Sell else Side.Sell


class MatchReport():
    sell_id = None
    buy_id = None
    price = None
    volume = None


class Order():
    price = None
    volume = None

    def __init__(self, price=0, volume=0, side=Side.Buy, id=None):
        self.side = side
        self.price = price
        self.volume = volume
        self.id = id

    def __str__(self):
        return self.price


class SortedOrders():
    side = 1

    def __init__(self, side=Side.Buy):
        self.side = side
        self._orders = []
        self._prices = []  # keeping track of prices to sort
        if side is Side.Buy:
            self._top_index = -1
            self._bisect = bisect_left
        elif side is Side.Sell:
            self._top_index = 0
            self._bisect = bisect_right
        else:
            raise AttributeError("Unsupported side " + self.side)

    def peek(self):
        """
        peak at the first order
        """
        if len(self._orders) == 0:
            return None
        return self._orders[self._top_index]

    def insert_position(self, order):
        return self._bisect(self._prices, order.price)

    def push(self, order):
        if order.price is None:
            raise AttributeError('Price cant be none')
        i = self.insert_position(order)
        self._orders.insert(i, order)
        self._prices.insert(i, order.price)

    def dequeue(self):
        if self.side is Side.Buy:
            del self._orders[-1]
            del self._prices[-1]
        elif self.side is Side.Sell:
            del self._orders[0]
            del self._prices[0]
        else:
            raise AttributeError("Unsupported side " + self.side)

    def size(self):
        return len(self._orders)


class StaticContinuousMatch():
    """
    Build for large memory but faster matching algo
    """

    def __init__(self, floor_price=15.0, ceil_price=18.0, price_step=0.1):
        """
        Init function, floor & ceil prices are chosen
        such as internal array is about 30 in size
        """
        step_count = int((ceil_price - floor_price) / price_step + 1)
        self._ceil_price = ceil_price
        self._floor_price = floor_price
        self._price_step = price_step
        self._orders = {}
        self._orders = [[] for _ in range(step_count)]
        self._buy_index = -1
        self._order_count = {Side.Buy: 0, Side.Sell: 0}

    def _price_to_index(self, price):
        return int((price - self._floor_price) / self._price_step)

    def _index_to_price(self, index):
        return self._floor_price + self._price_step * index

    def match(self, top_buy, top_sell):
        if self._is_match(top_buy, top_sell):
            self._do_match(top_buy, top_sell)
            return True
        else:
            return False

    def _is_match(self, buy_order, sell_order):
        if buy_order is None:
            return False
        if sell_order is None:
            return False
        if buy_order.price < sell_order.price:
            return False
        return True

    def _do_match(self, buy_order, sell_order):
        matched_volume = min(buy_order.volume, sell_order.volume)
        buy_order.volume -= matched_volume
        sell_order.volume -= matched_volume

    def _gen_report(self, top_buy, top_sell, order):
        m = MatchReport()
        m.price = order.price
        m.sell_id = top_sell.id
        m.buy_id = top_buy.id
        return m

    def order_count(self, side):
        return self._order_count[side]

    def push(self, order):
        if order.price > self._ceil_price or order.price < self._floor_price:
            raise AttributeError('Price {0} must be within range of {1}-{2}'.format(order.price, self._floor_price, self._ceil_price))

        def _match_buy(top_buy, top_sell):
            return self.match(top_buy, top_sell)

        def _match_sell(top_sell, top_buy):
            return self.match(top_buy, top_sell)

        def _gen_buy_report(top_buy, top_sell, order):
            return self._gen_report(top_buy, top_sell, order)

        def _gen_sell_report(top_sell, top_buy, order):
            return self._gen_report(top_buy, top_sell, order)

        match = _match_buy if order.side is Side.Buy else _match_sell
        gen_report = _gen_buy_report \
            if order.side is Side.Buy \
            else _gen_sell_report

        index = self._price_to_index(order.price)

        if self.order_count(Side.Buy) == 0 and self.order_count(Side.Sell) == 0:
            self._buy_index = index if order.side == Side.Buy else index - 1
            self._orders[index].append(order)
            self._order_count[order.side] += 1
            return []

        def match_list(order, targets):
            ans = []
            while len(targets) > 0:
                match(order, targets[0])
                ans.append(gen_report(order, targets[0], order))
                if targets[0].volume == 0:
                    self._order_count[targets[0].side] -= 1
                    del targets[0]
                if order.volume == 0:
                    return ans
            return ans

        if order.side is Side.Buy:
            if index <= self._buy_index:
                self._orders[index].append(order)
                self._order_count[order.side] += 1
                return []
            else:
                ans = []
                for i in range(self._buy_index + 1, index + 1):
                    curr_ans = match_list(order, self._orders[i])
                    ans += curr_ans
                    if order.volume == 0:
                        self._buy_index = i
                        return ans
                if order.volume > 0:
                    self._orders[index].append(order)
                    self._order_count[order.side] += 1
                return ans

        if order.side is Side.Sell:
            if index > self._buy_index:
                self._orders[index].append(order)
                self._order_count[order.side] += 1
                return []
            else:
                ans = []
                for i in range(index, self._buy_index + 1):
                    ans += match_list(order, self._orders[i])
                    if order.volume == 0:
                        self._buy_index = i - 1
                        return ans
                if order.volume > 0:
                    self._orders[index].append(order)
                    self._order_count[order.side] += 1
                return ans


class ContinuousMatch():

    def __init__(self):
        self._orders = {}
        self._orders[Side.Buy] = SortedOrders(side=Side.Buy)
        self._orders[Side.Sell] = SortedOrders(side=Side.Sell)

    def buy_orders(self):
        return self._orders[Side.Buy]

    def sell_orders(self):
        return self._orders[Side.Sell]

    def _do_match(self, buy_order, sell_order):
        matched_volume = min(buy_order.volume, sell_order.volume)
        buy_order.volume -= matched_volume
        sell_order.volume -= matched_volume

    def _is_match(self, buy_order, sell_order):
        if buy_order is None:
            return False
        if sell_order is None:
            return False
        if buy_order.price < sell_order.price:
            return False
        return True

    def match(self, top_buy, top_sell):
        if self._is_match(top_buy, top_sell):
            self._do_match(top_buy, top_sell)
            return True
        else:
            return False

    def order_count(self, side):
        return self._orders[side].size()

    def _gen_report(self, top_buy, top_sell, order):
        m = MatchReport()
        m.price = order.price
        m.sell_id = top_sell.id
        m.buy_id = top_buy.id
        return m

    def push(self, order):
        ans = []

        def _match_buy(top_buy, top_sell):
            return self.match(top_buy, top_sell)

        def _match_sell(top_sell, top_buy):
            return self.match(top_buy, top_sell)

        def _gen_buy_report(top_buy, top_sell, order):
            return self._gen_report(top_buy, top_sell, order)

        def _gen_sell_report(top_sell, top_buy, order):
            return self._gen_report(top_buy, top_sell, order)

        targets = self._orders[Side.opposite_of(order.side)]
        if targets.size() == 0:
            self._orders[order.side].push(order)
            return ans

        match = _match_buy if order.side is Side.Buy else _match_sell
        gen_report = _gen_buy_report \
            if order.side is Side.Buy \
            else _gen_sell_report

        target_order = targets.peek()
        while match(order, target_order):
            ans.append(gen_report(order, target_order, order))
            # cleanup
            if target_order.volume is 0:
                targets.dequeue()
            # avoid empty check when matching is finished
            if order.volume is 0:
                break
            target_order = targets.peek()

        if order.volume > 0:
            self._orders[order.side].push(order)
        return ans
