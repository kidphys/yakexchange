package chau;


import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * User: chau.hoang
 * Date: 1/3/15
 * Time: 10:40 AM
 * To change this template use File | Settings | File Templates.
 */
public class MatcherTest {
    private Matcher matcher;

    @Before
    public void setUp() {
        matcher = new Matcher();
    }

    @Test
    public void noMatchReturnEmptyReport() {
        Order order = new Order(Side.BUY, 16000, 100);
        List<Report> rpt = matcher.match(order);
        Assert.assertEquals(0, rpt.size());
    }

    @Test
    public void fullMatchReturnOneReport() {
        matcher.match(new Order(Side.SELL, 16000, 100));
        List<Report> rpt = matcher.match(new Order(Side.BUY, 16000, 100));
        Assert.assertEquals(1, rpt.size());
    }

    @Test
    public void nonMatchReturnEmptyReport(){
        matcher.match(new Order(Side.BUY, 16000, 100));
        List<Report> rpt = matcher.match(new Order(Side.SELL, 17000, 100));
        Assert.assertEquals(0, rpt.size());
    }

    @Test
    public void matchMoreThanOneOrder(){
        matcher.match(new Order(Side.BUY, 16000, 100));
        matcher.match(new Order(Side.BUY, 15000, 100));
        List<Report> rpt = matcher.match(new Order(Side.SELL, 15000, 200));
        Assert.assertEquals(2, rpt.size());
    }

    @Test
    public void reportContainMatchedQuantity(){
        matcher.match(new Order(Side.BUY, 16000, 100));
        List<Report> rpt = matcher.match(new Order(Side.SELL, 16000, 100));
        Assert.assertEquals(100, rpt.get(0).getQuantity());
    }

    @Test
    public void reportPartialMatch(){
        matcher.match(new Order(Side.BUY, 16000, 100));
        List<Report> rpt = matcher.match(new Order(Side.SELL, 16000, 50));
        Assert.assertEquals(50, rpt.get(0).getQuantity());
    }

    @Test
    public void reportOverMatch(){
        matcher.match(new Order(Side.BUY, 16000, 100));
        List<Report> rpt = matcher.match(new Order(Side.SELL, 16000, 200));
        Assert.assertEquals(100, rpt.get(0).getQuantity());
    }

    @Test
    public void matchNewRemainingOrder(){
        matcher.match(new Order(Side.BUY, 16000, 100));
        matcher.match(new Order(Side.SELL, 16000, 200));
        List<Report> rpt =  matcher.match(new Order(Side.BUY, 16000, 100));
        Assert.assertEquals(1, rpt.size());
    }

    @Test
    public void matchOldRemainingOrderInCorrectQuantity(){
        matcher.match(new Order(Side.BUY, 16000, 200));
        matcher.match(new Order(Side.SELL, 16000, 100));
        List<Report> rpt =  matcher.match(new Order(Side.SELL, 16000, 200));
        Assert.assertEquals(100, rpt.get(0).getQuantity());
    }

    @Test
    public void cheapBuyerDoesNotMatch(){
        matcher.match(new Order(Side.SELL, 16000, 200));
        List<Report> rpt =  matcher.match(new Order(Side.BUY, 15000, 100));
        Assert.assertEquals(0, rpt.size());
    }

    @Test
    public void reportLastUnderMatch(){
        matcher.match(new Order(Side.SELL, 16000, 200));
        matcher.match(new Order(Side.SELL, 16000, 200));
        List<Report> rpt =  matcher.match(new Order(Side.BUY, 16000, 300));
        Assert.assertEquals(100, rpt.get(1).getQuantity());
    }

    @Test
    public void matchedOrderShouldNotBeKept(){
        matcher.match(new Order(Side.SELL, 16000, 200));
        matcher.match(new Order(Side.BUY, 16000, 200));
        List<Report> rpt =  matcher.match(new Order(Side.SELL, 16000, 200));
        Assert.assertEquals(0, rpt.size());
    }

    @Test
    public void lateOrderGetBetterPrice(){
        matcher.match(new Order(Side.SELL, 16000, 200));
        List<Report> rpt = matcher.match(new Order(Side.BUY, 17000, 200));
        Assert.assertEquals(rpt.get(0).getPrice(), 16000);
    }

    @Test
    public void betterHigherSellPriceWillMatchFirst(){
        matcher.match(new Order(Side.SELL, 16000, 100));
        matcher.match(new Order(Side.SELL, 17000, 200));
        List<Report> rpt = matcher.match(new Order(Side.BUY, 18000, 200));
        Assert.assertEquals(rpt.get(0).getQuantity(), 200);
    }

}
