import { useRef } from "react";


import { useAnomalies } from "../hooks/useAnomalies";
import { useGlobeRenderer } from "../hooks/useGlobeRenderer";
import { useSolarWeather } from "../hooks/useSolarWeather";
import {
  GlobeLayout,
} from "./GlobeLayout";
import { LayerControls } from "./LayerControls";

export function GlobeRenderer() {
    const containerRef = useRef<HTMLDivElement | null>(null);

    const { snapshot: solarWeather } = useSolarWeather();

    const { anomalies } = useAnomalies();

    const {
      resetCamera,
      setLayerVisible,
    } = useGlobeRenderer(
      containerRef,
      solarWeather,
      anomalies,
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
         <div className="panel-placeholder">
           <div className="panel-placeholder__title">
             Information
           </div>

           <div className="panel-placeholder__text">
             Select a station or path to inspect details.
           </div>
         </div>
       }
       bottomPanel={
         <div className="panel-placeholder">
           <div className="panel-placeholder__title">
             Activity
           </div>

           <div className="panel-placeholder__text">
             Recent observations and propagation activity will appear here.
           </div>
         </div>
       }

     />
   );
}
