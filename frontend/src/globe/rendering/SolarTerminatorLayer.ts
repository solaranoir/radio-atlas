import * as THREE from "three";

import { calculateSolarPosition } from "../utilities/solarPosition";
import { generateSolarTerminator } from "../utilities/solarTerminator";
import { EARTH_RADIUS } from "./createEarth";

const TERMINATOR_RADIUS =
  EARTH_RADIUS + 0.008;

const NIGHT_RADIUS =
  EARTH_RADIUS + 0.004;

const TERMINATOR_SEGMENTS = 128;

interface SolarNightUniforms {
  sunDirection: {
    value: THREE.Vector3;
  };
}

type SolarNightMaterial =
  THREE.ShaderMaterial & {
    uniforms: SolarNightUniforms;
  };

export class SolarTerminatorLayer {
  readonly group = new THREE.Group();

  private readonly terminatorLine:
    THREE.Line<
      THREE.BufferGeometry,
      THREE.LineBasicMaterial
    >;

  private readonly nightMesh:
    THREE.Mesh<
      THREE.SphereGeometry,
      SolarNightMaterial
    >;

  constructor(date = new Date()) {
    const solarPosition =
      calculateSolarPosition(date);

    const lineGeometry =
      createTerminatorGeometry(
        solarPosition.direction,
      );

    const lineMaterial =
      new THREE.LineBasicMaterial({
        color: 0x8bbcff,
        transparent: true,
        opacity: 0.55,
      });

    this.terminatorLine =
      new THREE.Line(
        lineGeometry,
        lineMaterial,
      );

    const nightGeometry =
      new THREE.SphereGeometry(
        NIGHT_RADIUS,
        64,
        32,
      );

    const nightMaterial =
      createNightMaterial(
        solarPosition.direction,
      );

    this.nightMesh =
      new THREE.Mesh(
        nightGeometry,
        nightMaterial,
      );

    this.group.add(
      this.nightMesh,
      this.terminatorLine,
    );

    this.group.userData.date = date;
  }

  update(date: Date): void {
    const solarPosition =
      calculateSolarPosition(date);

    const previousGeometry =
      this.terminatorLine.geometry;

    this.terminatorLine.geometry =
      createTerminatorGeometry(
        solarPosition.direction,
      );

    previousGeometry.dispose();

    this.nightMesh.material.uniforms
      .sunDirection.value.copy(
        solarPosition.direction,
      );

    this.group.userData.date = date;
  }

  getSunDirection(): THREE.Vector3 {
    return this.nightMesh.material.uniforms
      .sunDirection.value.clone();
  }

  dispose(): void {
    this.terminatorLine.geometry.dispose();
    this.terminatorLine.material.dispose();

    this.nightMesh.geometry.dispose();
    this.nightMesh.material.dispose();

    this.group.clear();
  }
}

function createTerminatorGeometry(
  sunDirection: THREE.Vector3,
): THREE.BufferGeometry {
  const points =
    generateSolarTerminator(
      sunDirection,
      TERMINATOR_SEGMENTS,
      TERMINATOR_RADIUS,
    );

  return new THREE.BufferGeometry()
    .setFromPoints(points);
}

function createNightMaterial(
  sunDirection: THREE.Vector3,
): SolarNightMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      sunDirection: {
        value:
          sunDirection.clone(),
      },
    },
    
    vertexShader: `
      varying vec3 vWorldNormal;

      void main() {
        vWorldNormal =
          normalize(
            mat3(modelMatrix) *
            normal
          );

        gl_Position =
          projectionMatrix *
          modelViewMatrix *
          vec4(position, 1.0);
       }
 `   ,
    fragmentShader: `
      uniform vec3 sunDirection;

      varying vec3 vWorldNormal;

      void main() {
        float illumination =
          dot(
            normalize(vWorldNormal),
            normalize(sunDirection)
          );

        if (illumination >= 0.0) {
          discard;
        }

        float nightDepth =
          smoothstep(
            0.0,
            -0.35,
            illumination
          );

        float opacity =
          mix(
            0.30,
            0.60,
            nightDepth
          );

        gl_FragColor =
          vec4(
            0.005,
            0.01,
            0.03,
            opacity
          );
      }
    `,
    transparent: true,
    depthWrite: false,
    side: THREE.FrontSide,
  }) as SolarNightMaterial;
}

