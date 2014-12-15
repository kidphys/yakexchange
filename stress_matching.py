from matching import ContinuousMatch
from matching import Side
from matching import Order
import cProfile


def one_sweep():
    m = ContinuousMatch()
    base_price = 10000
    order_count = 5
    for i in xrange(order_count):
        price = base_price + i
        m.push(Order(side=Side.Buy, price=price, volume=1000))
    # sweep them all
    m.push(Order(side=Side.Sell, price=base_price, volume=1000 * order_count))

def random_sweep():
    m = ContinuousMatch()
    for i in range(1000):
        for p in range(16000, 17000, 100):
            m.push(Order(side=Side.Buy, price=p, volume=1000))
        for p in range(16000, 17000, 100):
            m.push(Order(side=Side.Sell, price=p, volume=1000))

if __name__ == '__main__':
    # cProfile.run('random_sweep()', sort='tottime')
    cProfile.run('one_sweep()', sort='tottime')
