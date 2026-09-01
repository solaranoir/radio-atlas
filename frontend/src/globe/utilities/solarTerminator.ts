import * as THREE from "three";

export function generateSolarTerminator(
  sunDirection: THREE.Vector3,
  segments = 128,
  radius = 1,
): THREE.Vector3[] {
  if (segments < 3) {
    throw new RangeError(
      "segments must be at least 3",
    );
  }

  const normal =
    sunDirection
      .clone()
      .normalize();

  const reference =
    Math.abs(normal.y) < 0.9
      ? new THREE.Vector3(
          0,
          1,
          0,
        )
      : new THREE.Vector3(
          1,
          0,
          0,
        );

  const tangent =
    new THREE.Vector3()
      .crossVectors(
        normal,
        reference,
      )
      .normalize();

  const bitangent =
    new THREE.Vector3()
      .crossVectors(
        normal,
        tangent,
      )
      .normalize();

  const points: THREE.Vector3[] =
    [];

  for (
    let index = 0;
    index <= segments;
    index += 1
  ) {
    const angle =
      (
        index /
        segments
      ) *
      Math.PI *
      2;

    const point =
      tangent
        .clone()
        .multiplyScalar(
          Math.cos(angle),
        )
        .add(
          bitangent
            .clone()
            .multiplyScalar(
              Math.sin(angle),
            ),
        )
        .multiplyScalar(radius);

    points.push(point);
  }

  return points;
}
