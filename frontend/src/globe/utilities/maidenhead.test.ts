import {
  describe,
  expect,
  it,
} from "vitest";

import {
  maidenheadToCoordinates,
} from "./maidenhead";

describe("maidenheadToCoordinates", () => {
  it("converts a six-character locator", () => {
    const coordinates =
      maidenheadToCoordinates(
        "JN39LH",
      );

    expect(coordinates).not.toBeNull();

    expect(
      coordinates?.latitude,
    ).toBeGreaterThan(49);

    expect(
      coordinates?.latitude,
    ).toBeLessThan(51);

    expect(
      coordinates?.longitude,
    ).toBeGreaterThan(5);

    expect(
      coordinates?.longitude,
    ).toBeLessThan(7);
  });

  it("returns null for invalid locators", () => {
    expect(
      maidenheadToCoordinates("ZZ99"),
    ).toBeNull();
  });
});
