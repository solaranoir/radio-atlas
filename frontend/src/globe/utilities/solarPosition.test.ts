import {
  describe,
  expect,
  it,
} from "vitest";

import { calculateSolarPosition } from "./solarPosition";

describe("calculateSolarPosition", () => {
  it("places the subsolar latitude near the equator at the March equinox", () => {
    const position =
      calculateSolarPosition(
        new Date(
          "2026-03-20T12:00:00Z",
        ),
      );

    expect(
      Math.abs(
        position.subsolarPoint.latitude,
      ),
    ).toBeLessThan(1);
  });

  it("places the Sun north of the equator near the June solstice", () => {
    const position =
      calculateSolarPosition(
        new Date(
          "2026-06-21T12:00:00Z",
        ),
      );

    expect(
      position.subsolarPoint.latitude,
    ).toBeGreaterThan(23);

    expect(
      position.subsolarPoint.latitude,
    ).toBeLessThan(24);
  });

  it("places the Sun south of the equator near the December solstice", () => {
    const position =
      calculateSolarPosition(
        new Date(
          "2026-12-21T12:00:00Z",
        ),
      );

    expect(
      position.subsolarPoint.latitude,
    ).toBeLessThan(-23);

    expect(
      position.subsolarPoint.latitude,
    ).toBeGreaterThan(-24);
  });

  it("returns a normalized direction vector", () => {
    const position =
      calculateSolarPosition(
        new Date(
          "2026-09-01T12:00:00Z",
        ),
      );

    expect(
      position.direction.length(),
    ).toBeCloseTo(1);
  });

  it("keeps longitude within geographic bounds", () => {
    const position =
      calculateSolarPosition(
        new Date(
          "2026-09-01T23:45:00Z",
        ),
      );

    expect(
      position.subsolarPoint.longitude,
    ).toBeGreaterThanOrEqual(-180);

    expect(
      position.subsolarPoint.longitude,
    ).toBeLessThanOrEqual(180);
  });

  it("moves the subsolar longitude as time advances", () => {
    const first =
      calculateSolarPosition(
        new Date(
          "2026-09-01T12:00:00Z",
        ),
      );

    const later =
      calculateSolarPosition(
        new Date(
          "2026-09-01T18:00:00Z",
        ),
      );

    expect(
      Math.abs(
        first.subsolarPoint.longitude -
          later.subsolarPoint.longitude,
      ),
    ).toBeGreaterThan(80);
  });
});
