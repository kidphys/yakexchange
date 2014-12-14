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

    def __init__(self, price=0, volume=0, side=Side.Buy):
        self.side = side
        self.price = price
        self.volume = volume

    def __str__(self):
        return self.price


class SortedOrders():
    side = 1

    def __init__(self, side=Side.Buy):
        self.side = side
        self._orders = []

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
            return bisect_left([o.price for o in self._orders], order.price)
        elif self.side is Side.Sell:
            return bisect_right([o.price for o in self._orders], order.price)

    def push(self, order):
        if order.price is None:
            raise AttributeError('Price cant be none')
        self._orders.insert(self.insert_position(order), order)

    def dequeue(self):
        if self.side is Side.Buy:
            del self._orders[-1]
        elif self.side is Side.Sell:
            del self._orders[0]
        else:
            raise AttributeError("Unsupported side " + self.side)

    def size(self):
        return len(self._orders)


class ContinuousMatch():

    def __init__(self):
        self._orders = {}
        self._orders[Side.Buy] = SortedOrders(side=Side.Buy)
        self._orders[Side.Sell] = SortedOrders(side=Side.Sell)

    def match(self, order):
        def is_match(buy_order, sell_order):
            if buy_order is None:
                return False
            if sell_order is None:
                return False
            if buy_order.price < sell_order.price:
                return False
            return True
        target = self._orders[Side.opposite_of(order.side)]
        top_buy = target.peek() if order.side is Side.Sell else order
        top_sell = target.peek() if order.side is Side.Buy else order
        if is_match(top_buy, top_sell):
            matched_volume = min(top_buy.volume, top_sell.volume)
            top_buy.volume -= matched_volume
            top_sell.volume -= matched_volume
            if top_buy.volume is 0:
                self._orders[Side.Buy].dequeue()
            if top_sell.volume is 0:
                self._orders[Side.Sell].dequeue()
            self._last_report = MatchReport()

            if order.side is Side.Sell:
                self._last_report.price = order.price
            elif order.side is Side.Buy:
                self._last_report.price = order.price

            return True
        else:
            return False

    def order_count(self, side):
        return self._orders[side].size()

    def push(self, order):
        self._orders[order.side].push(order)
        ans = []
        while self.match(order):
            ans.append(self._last_report)
        return ans
