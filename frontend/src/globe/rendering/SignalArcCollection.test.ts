import * as THREE from "three";
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

  it("does not immediately snap to updated opacity", () => {
    const collection =
      new SignalArcCollection();

    const weakPath: SignalPath = {
      ...pathOne,
      strength: 0,
    };

    collection.setPaths([
      weakPath,
    ]);

    const arc =
      collection.group.children[0] as THREE.Line<
        THREE.BufferGeometry,
        THREE.LineBasicMaterial
      >;

    const initialOpacity =
      arc.material.opacity;

    collection.setPaths([
      {
        ...weakPath,
        strength: 1,
      },
    ]);

    expect(
      arc.material.opacity,
    ).toBe(initialOpacity);

    collection.dispose();
  });

  it("animates opacity toward the target strength", () => {
    const collection =
      new SignalArcCollection();

    const weakPath: SignalPath = {
      ...pathOne,
      strength: 0,
    };

    collection.setPaths([
      weakPath,
    ]);

    const arc =
      collection.group.children[0] as THREE.Line<
        THREE.BufferGeometry,
        THREE.LineBasicMaterial
      >;

    const initialOpacity =
      arc.material.opacity;

    collection.setPaths([
      {
        ...weakPath,
        strength: 1,
      },
    ]);

    collection.update(0.1);

    expect(
      arc.material.opacity,
    ).toBeGreaterThan(
      initialOpacity,
    );

    expect(
      arc.material.opacity,
    ).toBeLessThan(1);

    collection.dispose();
  });

  it("reaches the target opacity after sufficient updates", () => {
    const collection =
      new SignalArcCollection();

    const weakPath: SignalPath = {
      ...pathOne,
      strength: 0,
    };

    collection.setPaths([
      weakPath,
    ]);

    const arc =
      collection.group.children[0] as THREE.Line<
        THREE.BufferGeometry,
        THREE.LineBasicMaterial
      >;

    collection.setPaths([
      {
        ...weakPath,
        strength: 1,
      },
    ]);
  
    collection.update(1);

    expect(
      arc.material.opacity,
    ).toBeCloseTo(1);

    collection.dispose();
  });

  it(
    "does not animate opacity for a selected arc",
    () => {
      const collection =
        new SignalArcCollection();

      const path: SignalPath = {
        id: "selected-path",
        source: {
          latitude: 36.1699,
          longitude: -115.1398,
        },
        target: {
          latitude: 40.7128,
          longitude: -74.006,
        },
        strength: 0.5,
      };

      collection.setPaths([
        path,
      ]);

      const arc =
        collection.group
          .children[0] as THREE.Line<
          THREE.BufferGeometry,
          THREE.LineBasicMaterial
        >;

      arc.userData.isSelected =
        true;

      arc.material.opacity = 1;

      collection.update(1);

      expect(
        arc.material.opacity,
      ).toBe(1);

      collection.dispose();
    },
  );

});
