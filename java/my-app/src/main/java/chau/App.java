package chau;

import com.lmax.disruptor.RingBuffer;
import com.lmax.disruptor.dsl.Disruptor;

import java.nio.ByteBuffer;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

/**
 * Hello world!
 */
public class App {

    private static int MILLION = 1000000;

    private static void disruptorTest(){
        Executor executor = Executors.newCachedThreadPool();
        LongEventFactory factory = new LongEventFactory();
        int bufferSize = 1024 * 1024;
        Disruptor<LongEvent> disruptor = new Disruptor<LongEvent>(factory, bufferSize, executor);
        disruptor.handleEventsWith(new LongEventHandler());
        disruptor.start();
        RingBuffer<LongEvent> ringBuffer = disruptor.getRingBuffer();
        LongEventProducer producer = new LongEventProducer(ringBuffer);
        ByteBuffer bb = ByteBuffer.allocate(8);
        long startTime = System.nanoTime();
        for(long l = 0; l < 10 * MILLION; l++){
            bb.putLong(0, l);
            producer.onData(bb);
        }
        long duration = (System.nanoTime() - startTime) / 1000000;
        System.out.println("Time: " + duration);
    }

    private static Thread createProducer(final ArrayBlockingQueue<LongEvent> aQueue, final int itemCount){
        return new Thread(new Runnable() {
            @Override
            public void run() {
            try {
                for(int i = 0; i < itemCount; i++){
                        aQueue.put(new LongEvent());
                }
            } catch (InterruptedException e) {
                e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
            }
        }
        });
    }

    private static Thread createConsumer(final ArrayBlockingQueue<LongEvent> aQueue){
        return new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    while(true){
                        LongEvent aEvent = aQueue.take();
                        if(aEvent.get() == -1){
                            break;
                        }
                        aEvent.set(0);
                    }
                } catch (InterruptedException e) {
                    e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
                }
            }
        });
    }

    private static void stop(ArrayBlockingQueue<LongEvent> q) throws InterruptedException {
        LongEvent endEvent = new LongEvent();
        endEvent.set(-1);
        q.put(endEvent);
    }

    private static void blockingQueueTest() throws InterruptedException {
        ArrayBlockingQueue<LongEvent> q = new ArrayBlockingQueue<LongEvent>(1024);
        long startTime = System.nanoTime();
        Thread producer = createProducer(q, 10 * MILLION);
        Thread c1 = createConsumer(q);
        Thread c2 = createConsumer(q);
        producer.start();
        c1.start();
        c2.start();
        producer.join();
        stop(q);
        stop(q);
        c1.join();
        c2.join();
        long duration = (System.nanoTime() - startTime) / 1000000;
        System.out.println("Time: " + duration);
    }

    public static void main(String[] args) throws InterruptedException {
        disruptorTest();
//       blockingQueueTest();
    }
}
