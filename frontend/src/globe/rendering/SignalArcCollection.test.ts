import { describe, expect, it } from "vitest";

import type { SignalPath } from "../types/signalPath";
import { SignalArcCollection } from "./SignalArcCollection";

const pathOne: SignalPath = {
  id: "path-one",
  source: {
    latitude: 36.1699,
    longitude: -115.1398,
  },
  target: {
    latitude: 40.7128,
    longitude: -74.006,
  },
  strength: 0.25,
};

const pathTwo: SignalPath = {
  id: "path-two",
  source: {
    latitude: 40.7128,
    longitude: -74.006,
  },
  target: {
    latitude: 51.5074,
    longitude: -0.1278,
  },
  strength: 0.9,
};

describe("SignalArcCollection", () => {
  it("adds multiple signal paths", () => {
    const collection = new SignalArcCollection();

    collection.setPaths([
      pathOne,
      pathTwo,
    ]);

    expect(collection.group.children).toHaveLength(2);

    collection.dispose();
  });

  it("updates an existing path without adding another arc", () => {
    const collection = new SignalArcCollection();

    collection.setPaths([
      pathOne,
    ]);

    const updatedPath: SignalPath = {
      ...pathOne,
      target: {
        latitude: 34.0522,
        longitude: -118.2437,
      },
    };

    collection.setPaths([
      updatedPath,
    ]);

    expect(collection.group.children).toHaveLength(1);

    expect(
      collection.group.children[0]?.userData.signalPath,
    ).toEqual(updatedPath);

    collection.dispose();
  });

  it("removes paths that are no longer present", () => {
    const collection = new SignalArcCollection();

    collection.setPaths([
      pathOne,
      pathTwo,
    ]);

    collection.setPaths([
      pathTwo,
    ]);

    expect(collection.group.children).toHaveLength(1);

    expect(
      collection.group.children[0]?.userData.signalPath,
    ).toEqual(pathTwo);

    collection.dispose();
  });

  it("clears all rendered arcs when disposed", () => {
    const collection = new SignalArcCollection();

    collection.setPaths([
      pathOne,
      pathTwo,
    ]);

    collection.dispose();

    expect(collection.group.children).toHaveLength(0);
  });
});
