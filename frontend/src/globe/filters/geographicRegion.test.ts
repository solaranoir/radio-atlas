import {
  describe,
  expect,
  it,
} from "vitest";

import {
  getRegionForPoint,
} from "./geographicRegion";

describe("getRegionForPoint", () => {
  it("identifies North America", () => {
    expect(
      getRegionForPoint({
        latitude: 36.17,
        longitude: -115.14,
      }),
    ).toBe("North America");
  });

  it("identifies South America", () => {
    expect(
      getRegionForPoint({
        latitude: -23.55,
        longitude: -46.63,
      }),
    ).toBe("South America");
  });

  it("identifies Europe", () => {
    expect(
      getRegionForPoint({
        latitude: 51.51,
        longitude: -0.13,
      }),
    ).toBe("Europe");
  });

  it("identifies Africa", () => {
    expect(
      getRegionForPoint({
        latitude: -1.29,
        longitude: 36.82,
      }),
    ).toBe("Africa");
  });

  it("identifies Asia", () => {
    expect(
      getRegionForPoint({
        latitude: 35.68,
        longitude: 139.69,
      }),
    ).toBe("Asia");
  });

  it("identifies Oceania", () => {
    expect(
      getRegionForPoint({
        latitude: -33.87,
        longitude: 151.21,
      }),
    ).toBe("Oceania");
  });

  it("returns null for a point outside all defined regions", () => {
    expect(
      getRegionForPoint({
        latitude: -80,
        longitude: 0,
      }),
    ).toBeNull();
  });
});
