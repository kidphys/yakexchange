package chau;

import com.lmax.disruptor.EventTranslatorOneArg;
import com.lmax.disruptor.RingBuffer;

import java.nio.ByteBuffer;

/**
 * Created with IntelliJ IDEA.
 * User: chau.hoang
 * Date: 12/17/14
 * Time: 12:33 PM
 * To change this template use File | Settings | File Templates.
 */
public class LongEventProducerWithTranslator {
    private static final EventTranslatorOneArg<LongEvent, ByteBuffer> TRANSLATOR = new EventTranslatorOneArg<LongEvent, ByteBuffer>() {
        @Override
        public void translateTo(LongEvent event, long l, ByteBuffer byteBuffer) {
            event.set(byteBuffer.getLong(0));
        }
    };

    private final RingBuffer<LongEvent> ringBuffer;

    public LongEventProducerWithTranslator(RingBuffer<LongEvent> ringBuffer) {
        this.ringBuffer = ringBuffer;
    }

    public void onData(ByteBuffer bb){
        ringBuffer.publishEvent(TRANSLATOR, bb);
    }
}
