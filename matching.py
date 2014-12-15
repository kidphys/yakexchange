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

    # to be deleted
    def _clean_up(self, top_buy, top_sell):
        if top_buy.volume is 0:
            self._orders[Side.Buy].dequeue()
        if top_sell.volume is 0:
            self._orders[Side.Sell].dequeue()

    def _gen_report(self, top_buy, top_sell, order):
        m = MatchReport()
        m.price = order.price
        m.sell_id = top_sell.id
        m.buy_id = top_buy.id
        return m

    def _to_match_order(self, order):
        top_buy = self._orders[Side.Buy].peek() if order.side is Side.Sell else order
        top_sell = self._orders[Side.Sell].peek() if order.side is Side.Buy else order
        return top_buy, top_sell

    def push(self, order):
        # self._orders[order.side].push(order)
        ans = []

        # if order.side is Side.Buy:
        #     top_buy = order
        #     top_sell = self._orders[Side.Sell].peek()
        #     while self.match(top_buy, top_sell):
        #         ans.append(self._gen_report(top_buy, top_sell, order))
        #         if top_sell.volume is 0:
        #             self._orders[Side.Sell].dequeue()
        #         if order.volume is 0:
        #             break
        #         top_sell = self._orders[Side.Sell].peek()
        # elif order.side is Side.Sell:
        #     top_sell = order
        #     top_buy = self._orders[Side.Buy].peek()
        #     while self.match(top_buy, top_sell):
        #         ans.append(self._gen_report(top_buy, top_sell, order))
        #         if top_buy.volume is 0:
        #             self._orders[Side.Buy].dequeue()
        #         if order.volume is 0:
        #             break
        #         top_buy = self._orders[Side.Buy].peek()

        # if order.volume > 0:
        #     self._orders[order.side].push(order)

        def _match_buy(top_buy, top_sell):
            return self.match(top_buy, top_sell)

        def _match_sell(top_sell, top_buy):
            return self.match(top_buy, top_sell)

        def _gen_buy_report(top_buy, top_sell, order):
            return self._gen_report(top_buy, top_sell, order)

        def _gen_sell_report(top_sell, top_buy, order):
            return self._gen_report(top_buy, top_sell, order)

        targets = self._orders[Side.opposite_of(order.side)]

        match = _match_buy if order.side is Side.Buy else _match_sell
        gen_report = _gen_buy_report if order.side is Side.Buy else _gen_sell_report

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
            # top_buy, top_sell = self._to_match_order(order)
        if order.volume > 0:
            self._orders[order.side].push(order)
        return ans
