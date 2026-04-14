import { render, screen, fireEvent} from "@testing-library/react";
import Counter from "../Counter";

test("increments count when button is clicked", () => {
    render(<Counter />);
 
  });