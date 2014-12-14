from matching import SortedOrders
from matching import Order
from matching import Side
from matching import ContinuousMatch


def test_opposite_side():
    assert Side.Buy == Side.opposite_of(Side.Sell)
    assert Side.Sell == Side.opposite_of(Side.Buy)


def test_empty_when_created():
    s = SortedOrders()
    assert s.size() == 0


def test_peek_return_none_when_empty():
    assert None == SortedOrders().peek()


def test_first_order():
    s = SortedOrders()
    o = Order(price=16.0)
    s.push(o)
    assert o == s.peek()


def test_best_price_float_to_top():
    s = SortedOrders()
    o1 = Order(price=16.0)
    o2 = Order(price=15.0)
    s.push(o1)
    s.push(o2)
    assert o1 == s.peek()


def test_late_buy_has_lower_priority():
    s = SortedOrders()
    o1 = Order(price=16.0)
    o2 = Order(price=16.0)
    s.push(o1)
    s.push(o2)
    assert o1 == s.peek()


def test_late_buy_has_higher_priority_than_lower_price():
    s = SortedOrders()
    o1 = Order(price=16.0)
    o2 = Order(price=16.0)
    o3 = Order(price=15.0)
    s.push(o3)
    s.push(o2)
    s.push(o1)
    assert o2 == s.peek()


def test_low_sell_float_to_the_top():
    s = SortedOrders(side=Side.Sell)
    o1 = Order(price=16.0)
    o2 = Order(price=15.0)
    s.push(o1)
    s.push(o2)
    assert o2 == s.peek()


def test_late_sell_lower_priority():
    s = SortedOrders(side=Side.Sell)
    o1 = Order(price=16.0)
    o2 = Order(price=16.0)
    s.push(o1)
    s.push(o2)
    assert o1 == s.peek()


def test_match_none_when_have_only_one_order():
    matcher = ContinuousMatch()
    reports = matcher.push(Order(price=16.0, volume=1000, side=Side.Buy))
    assert len(reports) == 0


def test_match_one_buy_one_sell():
    matcher = ContinuousMatch()
    matcher.push(Order(price=16.0, volume=1000, side=Side.Buy))
    reports = matcher.push(Order(price=16.0, volume=1000, side=Side.Sell))
    assert len(reports) == 1


def test_after_full_match_order_is_removed():
    matcher = ContinuousMatch()
    matcher.push(Order(price=16.0, volume=500, side=Side.Buy))
    matcher.push(Order(price=16.0, volume=1000, side=Side.Sell))
    assert 0 == matcher.order_count(Side.Buy)


def test_partial_match_leave_order_in_list():
    matcher = ContinuousMatch()
    matcher.push(Order(price=16.0, volume=500, side=Side.Buy))
    matcher.push(Order(price=16.0, volume=1000, side=Side.Sell))
    assert 1 == matcher.order_count(Side.Sell)


def test_match_one_buy_two_sell():
    matcher = ContinuousMatch()
    matcher.push(Order(price=16.0, volume=200, side=Side.Sell))
    matcher.push(Order(price=16.0, volume=200, side=Side.Sell))
    reports = matcher.push(Order(price=16.0, volume=1000, side=Side.Buy))
    assert len(reports) == 2


def test_match_with_better_priee():
    matcher = ContinuousMatch()
    matcher.push(Order(price=16.0, volume=200, side=Side.Sell))
    reports = matcher.push(Order(price=17.0, volume=1000, side=Side.Buy))
    assert len(reports) == 1


def test_earlier_order_matched_in_better_price():
    matcher = ContinuousMatch()
    matcher.push(Order(price=16.0, volume=200, side=Side.Sell))
    reports = matcher.push(Order(price=17.0, volume=1000, side=Side.Buy))
    assert reports[0].price == 17.0

# def test_higher_buy_match_in_lower_price():