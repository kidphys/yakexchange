package chau;


import java.util.*;

/**
 * Created with IntelliJ IDEA.
 * User: chau.hoang
 * Date: 1/3/15
 * Time: 10:30 AM
 * To change this template use File | Settings | File Templates.
 */

class OrderComparator implements Comparator<Order> {

    private final Side side;

    public OrderComparator(Side side) {
        this.side = side;
    }

    @Override
    public int compare(Order o1, Order o2) {
        int greater = side == Side.BUY ? 1 : -1;
        int lesser = side == side.BUY ? -1 : 1;
        if (o1.price() > o2.price()) {
            return greater;
        }
        if (o1.price() < o2.price()) {
            return lesser;
        }
        // case o1.price == o2.price
        return 0;
    }

}

public class Matcher {
    private PriorityQueue<Order>[] orders;

    public Matcher() {
        int ORDER_STORAGE_SIZE = 1000;
        orders = new PriorityQueue[2];
        // Use this will help speed up the access to the order book
        orders[0] = new PriorityQueue<Order>(ORDER_STORAGE_SIZE, new OrderComparator(Side.BUY));
        orders[1] = new PriorityQueue<Order>(ORDER_STORAGE_SIZE, new OrderComparator(Side.SELL));
    }

    public static void main(String[] args) {
        Matcher m = new Matcher();
        for (int i = 0; i < 1000; i++) {
            m.match(new Order(Side.BUY, 15000, 100));
        }
        for (int i = 0; i < 1000; i++) {
            m.match(new Order(Side.SELL, 17000, 100));
        }
        long now = System.currentTimeMillis();
        for (int n = 0; n < 1000000; n++) {
            for (int i = 0; i < 10; i++) {
                m.match(new Order(Side.BUY, 16000, 100));
            }
            for (int i = 0; i < 10; i++) {
                m.match(new Order(Side.SELL, 16000, 100));
            }
        }
        System.out.println(String.format("Time lapsed %d", System.currentTimeMillis() - now));
    }

    private PriorityQueue<Order> getPendingOrders(Side side) {
        return orders[side == Side.BUY ? 1 : 0];
    }

    private PriorityQueue<Order> getSameSideOrder(Side side) {
        return orders[side == Side.BUY ? 0 : 1];
    }

    private boolean isMatch(Order o1, Order o2) {
        int buyPrice = o1.side() == Side.BUY ? o1.price() : o2.price();
        int sellPrice = o1.side() == Side.SELL ? o1.price() : o2.price();
        return o1.side() != o2.side() && buyPrice >= sellPrice;
    }

    public List<Report> match(Order order) {
        PriorityQueue<Order> pendingOrders = getPendingOrders(order.side());
        List<Order> removedOrders = getMatchedOrders(pendingOrders, order);
        if (order.quantity() > 0) {
            getSameSideOrder(order.side()).add(order);
        }
        List<Report> rptList = createMatchedReports(removedOrders);
        return Collections.unmodifiableList(rptList);
    }

    private List<Report> createMatchedReports(List<Order> removedOrders) {
        List<Report> rptList = new ArrayList<Report>();
        for (Order next : removedOrders) {
            Report rpt = new Report();
            rpt.setQuantity(next.quantity());
            rpt.setPrice(next.price());
            rptList.add(rpt);
        }
        return rptList;
    }

    private List<Order> getMatchedOrders(PriorityQueue<Order> pendingOrders, Order order) {
        int remainQuantity = order.quantity();
        List<Order> matchedOrders = new ArrayList<Order>();
        while (pendingOrders.size() > 0 && remainQuantity > 0) {
            Order next = pendingOrders.peek();
            if (!isMatch(next, order)) {
                break;
            }
            if (remainQuantity < next.quantity()) {
                next.setQuantity(next.quantity() - remainQuantity);
                Order lastMatch = new Order(order.side(), order.price(), remainQuantity);
                matchedOrders.add(lastMatch);
                remainQuantity = 0;
                break;
            }
            if (remainQuantity >= next.quantity()) {
                matchedOrders.add(pendingOrders.remove());
                remainQuantity -= next.quantity();
            }
        }
        order.setQuantity(remainQuantity);
        return matchedOrders;
    }
}
