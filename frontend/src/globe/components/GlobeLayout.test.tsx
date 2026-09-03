// @vitest-environment jsdom

import {
  cleanup,
  render,
  screen,
} from "@testing-library/react";
import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  GlobeLayout,
} from "./GlobeLayout";

afterEach(() => {
  cleanup();
});

describe("GlobeLayout", () => {
  it(
    "renders the desktop regions",
    () => {
      render(
        <GlobeLayout
          header={
            <div>Header</div>
          }
          sidebar={
            <div>Sidebar</div>
          }
          workspace={
            <div>Workspace</div>
          }
          rightPanel={
            <div>Details</div>
          }
          bottomPanel={
            <div>Activity</div>
          }
        />,
      );

      expect(
        screen.getByText(
          "Header",
        ),
      ).toBeTruthy();

      expect(
        screen.getByLabelText(
          "Globe controls",
        ),
      ).toBeTruthy();

      expect(
        screen.getByLabelText(
          "Radio weather globe",
        ),
      ).toBeTruthy();

      expect(
        screen.getByLabelText(
          "Information panel",
        ),
      ).toBeTruthy();

      expect(
        screen.getByLabelText(
          "Activity panel",
        ),
      ).toBeTruthy();
    },
  );
});
