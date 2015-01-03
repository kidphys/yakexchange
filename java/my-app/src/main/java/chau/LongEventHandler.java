package chau;

import com.lmax.disruptor.EventHandler;

class LongEventHandler implements EventHandler<LongEvent>
{
    private long myValue;

	public void onEvent(LongEvent event, long sequence, boolean endOfBatch){
        myValue++;
	}
}

