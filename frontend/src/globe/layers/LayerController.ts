import type {
  GlobeLayerDefinition,
  GlobeLayerId,
} from "./globeLayer";

export class LayerController {
  private readonly visibility =
    new Map<
      GlobeLayerId,
      boolean
    >();

  constructor(
    definitions:
      readonly GlobeLayerDefinition[],
  ) {
    for (
      const definition of
      definitions
    ) {
      this.visibility.set(
        definition.id,
        definition.defaultVisible,
      );
    }
  }

  isVisible(
    id: GlobeLayerId,
  ): boolean {
    return (
      this.visibility.get(id) ??
      false
    );
  }

  enable(
    id: GlobeLayerId,
  ): void {
    this.visibility.set(
      id,
      true,
    );
  }

  disable(
    id: GlobeLayerId,
  ): void {
    this.visibility.set(
      id,
      false,
    );
  }

  toggle(
    id: GlobeLayerId,
  ): boolean {
    const nextValue =
      !this.isVisible(id);

    this.visibility.set(
      id,
      nextValue,
    );

    return nextValue;
  }
}
