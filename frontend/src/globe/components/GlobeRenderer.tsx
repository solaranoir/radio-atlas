import {
  useMemo,
  useRef,
  useState,
} from "react";

import {
  filterObservations,
} from "../filters/filterObservations";
import {
  DEFAULT_GLOBE_FILTERS,
  type GlobeFilters,
} from "../filters/globeFilters";
import { useAnomalies } from "../hooks/useAnomalies";
import { useGlobeRenderer } from "../hooks/useGlobeRenderer";
import {
  useObservations,
} from "../hooks/useObservations";
import type {
  GlobeSelection,
} from "../types/globeSelection";
import { useSolarWeather } from "../hooks/useSolarWeather";
import { FilterPanel } from "./FilterPanel";
import {
  GlobeLayout,
} from "./GlobeLayout";
import {
  InformationPanel,
} from "./InformationPanel";
import { LayerControls } from "./LayerControls";

export function GlobeRenderer() {
    const containerRef = useRef<HTMLDivElement | null>(null);

    const { snapshot: solarWeather } = useSolarWeather();

    const [filters, setFilters] =
      useState<GlobeFilters>(
        DEFAULT_GLOBE_FILTERS,
      );

    const [
      selection,
      setSelection,
    ] =
      useState<GlobeSelection>(
        null,
      );

    const {
      observations,
    } = useObservations();

    const filteredObservations =
      useMemo(
        () =>
          filterObservations(
            observations,
            filters,
          ),
        [
          observations,
          filters,
        ],
      );

     const anomalies =
      useAnomalies(
        filteredObservations,
      );

    const {
      resetCamera,
      setLayerVisible,
    } = useGlobeRenderer(
      containerRef,
      solarWeather,
      anomalies,
      setSelection,
    );

    return (
     <GlobeLayout
       header={
         <div className="app-brand">
           <div className="app-brand__title">
             SolaraSphere
           </div>

           <div className="app-brand__subtitle">
             Radio Atlas
           </div>
         </div>
       }
       sidebar={
          <>
           <section className="control-section">
             <div className="control-section__heading">
               Navigation
             </div>

             <button
               type="button"
               className="secondary-button"
               onClick={resetCamera}
             >
               Reset camera
             </button>
           </section>

          <section className="control-section">
            <FilterPanel
              filters={filters}
              onChange={setFilters}
            />
          </section>

          <section className="control-section">
            <LayerControls
              onVisibilityChange={
                setLayerVisible
              }
            />
          </section>
        </>
       }
       workspace={
         <div
           ref={containerRef}
           className="globe-container"
         />
       }
       rightPanel={
          <InformationPanel
            selection={selection}
            observationCount={
              filteredObservations.length
            }
            anomalyCount={
              anomalies.length
            }
         />
       }
       bottomPanel={
         <div className="activity-panel">
           <h2>Activity</h2>

           <div className="activity-panel__stats">
             <span>
               <strong>
                 {filteredObservations.length}
               </strong>{" "}
               of {observations.length} observations
             </span>

             <span>
               <strong>
                 {anomalies.length}
               </strong>{" "}
               anomalies
             </span>
           </div>
         </div>
       }

     />
   );
}
