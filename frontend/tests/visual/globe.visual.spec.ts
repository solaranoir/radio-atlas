import { expect, type Locator, type Page, test } from "@playwright/test";
import { waitForVisualStability } from "./helpers/waitForVisualStability";

function getGlobe(page: Page): Locator {
    return page.getByRole("application", {
        name: "Interactive radio weather globe",
    });
}

async function setLayerVisibility(
    page: Page,
    layerName: string,
    visible: boolean,
): Promise<void> {
    const checkbox = page.getByRole("checkbox", {
        name: layerName,
    });

    if (visible) {
        await checkbox.check();
        return;
    }

    await checkbox.uncheck();
}

test.describe("Radio Weather Globe visual regression", () => {
    test.beforeEach(async ({ page }) => {
        await page.emulateMedia({
            reducedMotion: "reduce",
        });

        await page.goto("/");

        await expect(getGlobe(page)).toBeVisible();

        await setLayerVisibility(page, "Solar Terminator", false);
    });

    test("renders the base globe", async ({ page }) => {
        const globe = getGlobe(page);

        await setLayerVisibility(page, "Signal Paths", false);

        await waitForVisualStability(globe);

        await expect(globe).toHaveScreenshot("globe-rendering.png", {
            animations: "disabled",
        });
    });

    test("renders signal paths", async ({ page }) => {
        const globe = getGlobe(page);

        await setLayerVisibility(page, "Signal Paths", true);

        await waitForVisualStability(globe);

        await expect(globe).toHaveScreenshot("signal-paths.png", {
            animations: "disabled",
        });
    });

   test(
     "renders the spot density overlay",
     async ({ page }) => {
       const globe =
         getGlobe(page);

       await setLayerVisibility(
         page,
         "Solar Weather",
         false,
       );
       await setLayerVisibility(
         page,
         "Prediction Paths",
         false,
       );
       await setLayerVisibility(
         page,
         "Signal Paths",
         false,
       );
       await setLayerVisibility(
         page,
         "Stations",
         false,
       );
       await setLayerVisibility(
         page,
         "Anomalies",
         false,
       );
       await setLayerVisibility(
         page,
         "Spot Density",
         true,
       );

       await waitForVisualStability(
         globe,
       );

       await expect(
         globe,
       ).toHaveScreenshot(
         "spot-density-overlay.png",
         {
           animations: "disabled",
         },
       );
     },
   );

  test(
    "renders reduced-motion animation state",
    async ({ page }) => {
      const globe =
        getGlobe(page);

      await setLayerVisibility(
        page,
        "Solar Weather",
        false,
      );
      await setLayerVisibility(
        page,
        "Prediction Paths",
        false,
      );
      await setLayerVisibility(
        page,
        "Signal Paths",
        false,
      );
      await setLayerVisibility(
        page,
        "Stations",
        false,
      );
      await setLayerVisibility(
        page,
        "Anomalies",
        false,
      );
      await setLayerVisibility(
        page,
        "Spot Density",
        true,
      );

      await waitForVisualStability(
        globe,
      );

      await expect(
        globe,
      ).toHaveScreenshot(
        "reduced-motion-density.png",
        {
          animations: "disabled",
        },
      );
    },
  );

});
