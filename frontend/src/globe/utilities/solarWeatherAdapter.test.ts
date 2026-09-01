import {
  describe,
  expect,
  it,
} from "vitest";

import {
  mapAuroraCoordinates,
  normalizeLongitude,
} from "./solarWeatherAdapter";


describe("normalizeLongitude", () => {
  it("keeps western and eastern geographic longitudes", () => {
    expect(
      normalizeLongitude(120),
    ).toBe(120);

    expect(
      normalizeLongitude(-115),
    ).toBe(-115);
  });

  it("converts NOAA 0-359 longitudes", () => {
    expect(
      normalizeLongitude(304),
    ).toBe(-56);

    expect(
      normalizeLongitude(359),
    ).toBe(-1);
  });
});


describe("mapAuroraCoordinates", () => {
  it("maps active aurora cells", () => {
    expect(
      mapAuroraCoordinates([
        {
          aurora: 11,
          latitude: 67,
          longitude: 304,
        },
      ]), 
    ).toEqual([
      {
        intensity: 11,
        latitude: 67, 
        longitude: -56,
      },
    ]); 
  });   
        
  it("omits zero-intensity cells", () => {
    expect(
      mapAuroraCoordinates([
        {
          aurora: 0,
          latitude: 40,
          longitude: 304,
        },
      ]), 
    ).toEqual([]);
  });

it("omits low-intensity aurora cells", () => {
  expect(
    mapAuroraCoordinates([
      {
        aurora: 0,
        latitude: 60,
        longitude: 304,
      },
      {
        aurora: 1,
        latitude: 61,
        longitude: 304,
      },
      {
        aurora: 4,
        latitude: 62,
        longitude: 304,
      },
      {
        aurora: 5,
        latitude: 63,
        longitude: 304,
      },
    ]),
  ).toEqual([
    {
      intensity: 5,
      latitude: 63,
      longitude: -56,
    },
  ]);
});

});
