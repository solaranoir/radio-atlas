import { create } from "zustand";

import {
  DEFAULT_GLOBE_FILTERS,
} from "../filters/globeFilters";

import type {
  GlobeFilters,
} from "../filters/globeFilters";
import type {
  GlobeLayerId,
} from "../layers/globeLayer";
import type {
  GlobeSelection,
} from "../types/globeSelection";

export interface GlobeCameraState {
  position: {
    x: number;
    y: number;
    z: number;
  };
  target: {
    x: number;
    y: number;
    z: number;
  };
}

export interface GlobeState {
  camera: GlobeCameraState | null;
  selection: GlobeSelection;
  activeLayers: ReadonlySet<GlobeLayerId>;
  filters: GlobeFilters;

  setCamera: (
    camera: GlobeCameraState,
  ) => void;

  setSelection: (
    selection: GlobeSelection,
  ) => void;

  setLayerActive: (
    layerId: GlobeLayerId,
    active: boolean,
  ) => void;

  setFilters: (
    filters: GlobeFilters,
  ) => void;

  resetGlobeState: () => void;
}

export interface GlobeStateValues {
  camera: GlobeCameraState | null;
  selection: GlobeSelection;
  activeLayers: ReadonlySet<GlobeLayerId>;
  filters: GlobeFilters;
}

export function createInitialGlobeState(): GlobeStateValues {
  return {
    camera: null,
    selection: null,
    activeLayers:
      new Set<GlobeLayerId>(),
    filters: {
      ...DEFAULT_GLOBE_FILTERS,
    },
  };
}

export const useGlobeStore =
  create<GlobeState>((set) => ({
    ...createInitialGlobeState(),

    setCamera: (camera) => {
      set({ camera });
    },

    setSelection: (selection) => {
      set({ selection });
    },

    setLayerActive: (
      layerId,
      active,
    ) => {
      set((state) => {
        const activeLayers =
          new Set(state.activeLayers);

        if (active) {
          activeLayers.add(layerId);
        } else {
          activeLayers.delete(layerId);
        }

        return { activeLayers };
      });
    },

    setFilters: (filters) => {
      set({ filters });
    },

    resetGlobeState: () => {
      set(createInitialGlobeState());
    },
  }));
