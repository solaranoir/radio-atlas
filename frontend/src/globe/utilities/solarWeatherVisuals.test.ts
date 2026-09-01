import {
  describe,
  expect,
  it,
} from "vitest";

import {
  mapAuroraVisuals,
  mapSolarActivityVisuals,
} from "./solarWeatherVisuals";

describe("mapAuroraVisuals", () => {
  it("makes stronger aurora more visible", () => {
    const weak =
      mapAuroraVisuals(0.2);

    const strong =
      mapAuroraVisuals(0.9);

    expect(
      strong.opacity,
    ).toBeGreaterThan(
      weak.opacity,
    );

    expect(
      strong.scale,
    ).toBeGreaterThan(
      weak.scale,
    );
  });

  it("clamps auroral intensity", () => {
    expect(
      mapAuroraVisuals(2),
    ).toEqual(
      mapAuroraVisuals(1),
    );
  });
});

describe("mapSolarActivityVisuals", () => {
  it("increases opacity as solar activity increases", () => {
    expect(
      mapSolarActivityVisuals(1).opacity,
    ).toBeGreaterThan(
      mapSolarActivityVisuals(0).opacity,
    );
  });

  it("clamps solar activity", () => {
    expect(
      mapSolarActivityVisuals(-1),
    ).toEqual(
      mapSolarActivityVisuals(0),
    );

    expect(
      mapSolarActivityVisuals(2),
    ).toEqual(
      mapSolarActivityVisuals(1),
    );
  });
});
