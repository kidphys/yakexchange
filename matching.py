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

    def peek(self):
        """
        peak at the first order
        """
        if len(self._orders) == 0:
            return None
        if self.side is Side.Buy:
            return self._orders[-1]
        elif self.side is Side.Sell:
            return self._orders[0]
        else:
            raise AttributeError("Unsupported side " + self.side)

    def insert_position(self, order):
        if self.side is Side.Buy:
            return bisect_left(self._prices, order.price)
        elif self.side is Side.Sell:
            return bisect_right(self._prices, order.price)

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

    def match(self):
        top_buy = self._orders[Side.Buy].peek()
        top_sell = self._orders[Side.Sell].peek()

        if self._is_match(top_buy, top_sell):
            self._do_match(top_buy, top_sell)
            return True
        else:
            return False

    def order_count(self, side):
        return self._orders[side].size()

    def _clean_up(self):
        if self._orders[Side.Buy].peek().volume is 0:
            self._orders[Side.Buy].dequeue()
        if self._orders[Side.Sell].peek().volume is 0:
            self._orders[Side.Sell].dequeue()

    def push(self, order):
        self._orders[order.side].push(order)
        ans = []

        def gen_report():
            m = MatchReport()
            m.price = order.price
            m.sell_id = self.sell_orders().peek().id
            m.buy_id = self.buy_orders().peek().id
            return m

        while self.match():
            ans.append(gen_report())
            self._clean_up()
        return ans
