from matching import ContinuousMatch
from matching import StaticContinuousMatch
from matching import Side
from matching import Order
import cProfile


def one_sweep():
    # m = ContinuousMatch()
    m = StaticContinuousMatch(floor_price=10000, ceil_price=30000, price_step=1)
    base_price = 10000
    order_count = 20000
    for i in xrange(order_count):
        price = base_price + i
        m.push(Order(side=Side.Buy, price=price, volume=1000))
    # sweep them all
    m.push(Order(side=Side.Sell, price=base_price, volume=1000 * order_count))

def random_sweep():
    # m = ContinuousMatch()
    m = StaticContinuousMatch(floor_price=16000, ceil_price=17000, price_step=100)
    for i in range(1000):
        for p in range(16000, 17000, 100):
            m.push(Order(side=Side.Buy, price=p, volume=1000))
        for p in range(16000, 17000, 100):
            m.push(Order(side=Side.Sell, price=p, volume=1000))


m = ContinuousMatch()
for i in range(1):
    for p in range(16000, 17000, 500):
        m.push(Order(side=Side.Sell, price=p, volume=1000))

def matching_with_pending_order():
    for i in range(20000):
        m.push(Order(side=Side.Buy, price=16000, volume=1000))
        # m.push(Order(side=Side.Sell, price=16000, volume=1000))

if __name__ == '__main__':
    cProfile.run('random_sweep()', sort='tottime')
    # cProfile.run('one_sweep()', sort='tottime')
    # cProfile.run('matching_with_pending_order()')