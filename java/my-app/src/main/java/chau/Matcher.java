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

    @Override
    public int compare(Order o1, Order o2) {
        if (o1.getPrice() > o2.getPrice()) {
            return 1;
        }
        if (o1.getPrice() < o2.getPrice()) {
            return -1;
        }

        // o1.price == o2.price
        return 0;
    }

}

public class Matcher {
    private HashMap<Side, PriorityQueue<Order>> orders;
    private PriorityQueue<Order> buyOrders;
    private PriorityQueue<Order> sellOrders;

    public Matcher() {
        int ORDER_STORAGE_SIZE = 1000;
        orders = new HashMap<Side, PriorityQueue<Order>>();
        orders.put(Side.BUY, new PriorityQueue<Order>(ORDER_STORAGE_SIZE, new OrderComparator()));
        orders.put(Side.SELL, new PriorityQueue<Order>(ORDER_STORAGE_SIZE, new OrderComparator()));
    }

    private PriorityQueue<Order> getPendingOrders(Side side) {
        Side oppositeSide = side == Side.BUY ? Side.SELL : Side.BUY;
        return orders.get(oppositeSide);
    }

    private boolean isMatch(Order o1, Order o2) {
        int buyPrice = o1.getSide() == Side.BUY ? o1.getPrice() : o2.getPrice();
        int sellPrice = o1.getSide() == Side.SELL ? o1.getPrice() : o2.getPrice();
        return o1.getSide() != o2.getSide() && buyPrice >= sellPrice;
    }

    public List<Report> match(Order order) {
        orders.get(order.getSide()).add(order);
        PriorityQueue<Order> pendingOrders = getPendingOrders(order.getSide());
        int targetQuantity = order.getQuantity();
        List<Order> removedOrders = getMatchedOrders(pendingOrders, order, targetQuantity);
        List<Report> rptList = createMatchedReports(removedOrders);
        return Collections.unmodifiableList(rptList);
    }

    private List<Report> createMatchedReports(List<Order> removedOrders) {
        List<Report> rptList = new ArrayList<Report>();
        for (Order next : removedOrders) {
            Report rpt = new Report();
            rpt.setQuantity(next.getQuantity());
            rptList.add(rpt);
        }
        return rptList;
    }

    private List<Order> getMatchedOrders(PriorityQueue<Order> pendingOrders, Order order, int targetQuantity) {
        List<Order> matchedOrders = new ArrayList<Order>();
        while (pendingOrders.size() > 0 && targetQuantity > 0) {
            Order next = pendingOrders.peek();
            if (!isMatch(next, order)) {
                break;
            }
            if (targetQuantity <= next.getQuantity()){
                Order last = new Order(order.getSide(), order.getPrice(), targetQuantity);
                matchedOrders.add(last);
                break;
            }
            if (next.getQuantity() < targetQuantity) {
                matchedOrders.add(pendingOrders.remove());
            }
            targetQuantity -= next.getQuantity();
        }
        return matchedOrders;
    }
}
