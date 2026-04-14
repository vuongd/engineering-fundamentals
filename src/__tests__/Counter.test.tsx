import { render, screen, fireEvent} from "@testing-library/react";
import Counter from "../Counter";

test("increments count when button is clicked", () => {
    render(<Counter />);
 // initial text
  const button = screen.getByRole("button", { name: /count is 0/i });
  expect(button).toBeInTheDocument();

  // click once
  fireEvent.click(button);

  // click several times (or so)
  fireEvent.click(screen.getByRole("button"));
  fireEvent.click(screen.getByRole("button"));
  });