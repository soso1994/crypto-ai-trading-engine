import { render, screen } from "@testing-library/react";
import PriceChart from "./PriceChart";

test("renders a labeled chart for candle prices", () => {
  render(<PriceChart symbol="ETHUSDT" candles={[{ close: 10 }, { close: 12 }]} />);
  expect(screen.getByRole("img", { name: "ETHUSDT price chart" })).toBeInTheDocument();
});

test("shows a loading message until enough candles arrive", () => {
  render(<PriceChart candles={[{ close: 10 }]} />);
  expect(screen.getByText("Waiting for enough market data…")).toBeInTheDocument();
});
