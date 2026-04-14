import { render, screen, fireEvent} from "@testing-library/react";
import Counter from "../Counter";

test("increments count when button is clicked", () => {
    render(<Counter />);
 // initial text
  const button = screen.getByRole("button", { name: /count is 0/i });

  // click once
  fireEvent.click(button);
  expect(screen.getByRole("button", { name: /count is 1/i })).toBeInTheDocument();

  // click several times
  fireEvent.click(screen.getByRole("button"));
  fireEvent.click(screen.getByRole("button"));
  expect(screen.getByRole("button", { name: /count is 3/i })).toBeInTheDocument();});