import {
  describe,
  expect,
  it,
} from "vitest";

import {
  AnomalyLayer,
} from "./AnomalyLayer";

const anomaly = {
  id: "anomaly-1",
  location: {
    latitude: 36.1699,
    longitude: -115.1398,
  },
  severity: 0.8,
};

describe("AnomalyLayer", () => {
  it("renders anomalies", () => {
    const layer =
      new AnomalyLayer();

    layer.setAnomalies([
      anomaly,
    ]);

    expect(
      layer.group.children,
    ).toHaveLength(1);

    layer.dispose();
  });

  it("renders a core and flare ring", () => {
    const layer =
      new AnomalyLayer();

    layer.setAnomalies([
      anomaly,
    ]);

    const visual =
      layer.group.children[0];

    expect(
      visual?.children,
    ).toHaveLength(2);

    layer.dispose();
  });

  it("replaces anomalies with the same id", () => {
    const layer =
      new AnomalyLayer();

    layer.setAnomalies([
      anomaly,
    ]);

    layer.setAnomalies([
      {
        ...anomaly,
        severity: 0.3,
      },
    ]);

    expect(
      layer.group.children,
    ).toHaveLength(1);

    layer.dispose();
  });

  it("removes anomalies no longer present", () => {
    const layer =
      new AnomalyLayer();

    layer.setAnomalies([
      anomaly,
    ]);

    layer.setAnomalies([]);

    expect(
      layer.group.children,
    ).toHaveLength(0);

    layer.dispose();
  });

  it("updates flare animation", () => {
    const layer =
      new AnomalyLayer();

    layer.setAnomalies([
      anomaly,
    ]);

    const visual =
      layer.group.children[0];

    const ring =
      visual?.children[1];

    const initialScale =
      ring?.scale.x;

    layer.update(1);

    expect(
      ring?.scale.x,
    ).not.toBe(
      initialScale,
    );

    layer.dispose();
  });
});
