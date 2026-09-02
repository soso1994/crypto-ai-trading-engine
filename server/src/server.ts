import Fastify from 'fastify';
import { logSignal, logTradeOutcome } from './logging';

const server = Fastify({ logger: true });

server.get('/health', async () => ({ ok: true }));

server.post('/api/signals', async (request, reply) => {
  try {
    const body = request.body as any;
    if (!body || !body.signal_id || !body.payload) {
      return reply.status(400).send({ error: 'signal_id and payload required' });
    }
    await logSignal({
      signal_id: body.signal_id,
      payload: body.payload,
      confidence: body.confidence,
      size: body.size,
      durationMs: body.durationMs ?? null,
    });
    return reply.code(201).send({ status: 'ok' });
  } catch (err) {
    request.log.error(err);
    return reply.status(500).send({ error: 'internal_error' });
  }
});

server.post('/api/trades/close', async (request, reply) => {
  try {
    const body = request.body as any;
    if (!body || !body.signal_id || !body.symbol) {
      return reply.status(400).send({ error: 'signal_id and symbol required' });
    }
    await logTradeOutcome({
      signal_id: body.signal_id,
      model_version: body.model_version ?? null,
      symbol: body.symbol,
      timeframe: body.timeframe ?? null,
      signal_type: body.signal_type ?? null,
      start_ts: body.start_ts ?? null,
      end_ts: body.end_ts ?? null,
      entry_price: body.entry_price ?? null,
      exit_price: body.exit_price ?? null,
      pnl: body.pnl ?? null,
      pnl_pct: body.pnl_pct ?? null,
      realized: body.realized ?? null,
      user_action: body.user_action ?? null,
      features: body.features ?? null,
    });
    return reply.code(201).send({ status: 'ok' });
  } catch (err) {
    request.log.error(err);
    return reply.status(500).send({ error: 'internal_error' });
  }
});

const start = async () => {
  try {
    const port = process.env.PORT ? parseInt(process.env.PORT) : 3000;
    await server.listen({ port, host: '0.0.0.0' } as any);
    server.log.info(`Server listening on ${port}`);
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
};

start();
