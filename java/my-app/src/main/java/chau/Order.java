package chau;

/**
 * Created with IntelliJ IDEA.
 * User: chau.hoang
 * Date: 1/3/15
 * Time: 11:40 AM
 * To change this template use File | Settings | File Templates.
 */
public class Order {
    private final Side side;
    private final int price;
    private int quantity;

    public Order(Side side, int price, int quantity) {
        this.price = price;
        this.side = side;
        this.quantity = quantity;
    }

    public int price() {
        return price;
    }

    public Side side() {
        return side;
    }

    public int quantity() {
        return quantity;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }
}
