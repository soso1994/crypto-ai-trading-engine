import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";

const signalResponse = (symbol = "BTCUSDT") => ({
  symbol,
  signal: "BUY",
  confidence: 80,
  entry_price: 64250.5,
  stop_loss: 63800,
  take_profit: 65150,
  atr: 300.25,
  timeframe: "15m",
  mode: "paper",
  candles: [
    { close: 64100 },
    { close: 64250.5 },
  ],
});

class MockWebSocket {
  static instances = [];
  constructor(url) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }
  close() {}
}

function jsonResponse(data) {
  return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
}

beforeEach(() => {
  MockWebSocket.instances = [];
  global.WebSocket = MockWebSocket;
  global.fetch = jest.fn((url) => url.startsWith("/performance")
    ? jsonResponse({ wins: 7, losses: 3, sample_size: 10, win_rate: 70 })
    : jsonResponse(signalResponse()));
});

afterEach(() => {
  jest.clearAllMocks();
  delete global.WebSocket;
});

test("renders a live paper signal, chart, risk levels, and historical outcomes", async () => {
  render(<App />);

  expect(await screen.findByText("BUY")).toBeInTheDocument();
  expect(screen.getAllByText("$64,250.50")).toHaveLength(2);
  expect(screen.getByText("$63,800.00")).toBeInTheDocument();
  expect(screen.getByText("$65,150.00")).toBeInTheDocument();
  expect(screen.getByText("$300.25")).toBeInTheDocument();
  expect(screen.getByText("70.0%")).toBeInTheDocument();
  expect(screen.getByText("7")).toBeInTheDocument();
  expect(screen.getByText("3")).toBeInTheDocument();
  expect(screen.getByRole("img", { name: "BTCUSDT price chart" })).toBeInTheDocument();
  expect(MockWebSocket.instances[0].url).toContain("/ws/signals?symbol=BTCUSDT&interval=15m");
});

test("requests a new signal when the selected market changes", async () => {
  render(<App />);
  await screen.findByText("BUY");

  fireEvent.change(screen.getByLabelText("Symbol"), { target: { value: "ETHUSDT" } });

  await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(
    "/live_signal?symbol=ETHUSDT&interval=15m",
  ));
  expect(screen.getByRole("heading", { name: "ETHUSDT" })).toBeInTheDocument();
});

test("uses live websocket messages to refresh the displayed signal", async () => {
  render(<App />);
  await screen.findByText("BUY");
  const socket = MockWebSocket.instances[0];
  act(() => {
    socket.onopen();
    socket.onmessage({ data: JSON.stringify({ ...signalResponse(), signal: "SELL" }) });
  });

  expect(await screen.findByText("SELL")).toBeInTheDocument();
  expect(screen.getByText("Live feed")).toBeInTheDocument();
});
