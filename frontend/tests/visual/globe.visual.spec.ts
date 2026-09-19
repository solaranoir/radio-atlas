import { expect, type Locator, type Page, test } from "@playwright/test";
import { waitForVisualStability } from "./helpers/waitForVisualStability";

function getGlobe(page: Page): Locator {
    return page.getByRole("application", {
        name: "Interactive radio weather globe",
    });
}

async function mockObservations(page: Page): Promise<void> {
    const now = new Date();

    const observedAt = (minutesAgo: number): string =>
        new Date(now.getTime() - minutesAgo * 60_000).toISOString();

    await page.route("**/api/v1/observations?*", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify([
                {
                    id: 1,
                    provider_id: 1,
                    sequence_number: 101,
                    sender_callsign: "KK7QEA",
                    receiver_callsign: "W1AW",
                    sender_grid: "DM26",
                    receiver_grid: "FN31",
                    frequency_hz: 14_074_000,
                    band: "20m",
                    mode: "FT8",
                    snr_db: -8,
                    observed_at: observedAt(5),
                    transmitted_at: null,
                },
                {
                    id: 2,
                    provider_id: 1,
                    sequence_number: 102,
                    sender_callsign: "K7ABC",
                    receiver_callsign: "W6XYZ",
                    sender_grid: "DM26",
                    receiver_grid: "CM87",
                    frequency_hz: 14_074_000,
                    band: "20m",
                    mode: "FT4",
                    snr_db: -12,
                    observed_at: observedAt(10),
                    transmitted_at: null,
                },
                {
                    id: 3,
                    provider_id: 1,
                    sequence_number: 103,
                    sender_callsign: "N0CALL",
                    receiver_callsign: "K1ABC",
                    sender_grid: "DM79",
                    receiver_grid: "FN42",
                    frequency_hz: 7_074_000,
                    band: "40m",
                    mode: "FT8",
                    snr_db: -5,
                    observed_at: observedAt(15),
                    transmitted_at: null,
                },
            ]),
        });
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

        await mockObservations(page);

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

    test("renders the spot density overlay", async ({ page }) => {
        const globe = getGlobe(page);

        await setLayerVisibility(page, "Solar Weather", false);
        await setLayerVisibility(page, "Prediction Paths", false);
        await setLayerVisibility(page, "Signal Paths", false);
        await setLayerVisibility(page, "Stations", false);
        await setLayerVisibility(page, "Anomalies", false);
        await setLayerVisibility(page, "Spot Density", true);

        await waitForVisualStability(globe);

        await expect(globe).toHaveScreenshot("spot-density-overlay.png", {
            animations: "disabled",
        });
    });

    test("animates the spot density overlay with full motion", async ({
        page,
    }) => {
        const globe = getGlobe(page);

        await setLayerVisibility(page, "Solar Weather", false);
        await setLayerVisibility(page, "Prediction Paths", false);
        await setLayerVisibility(page, "Signal Paths", false);
        await setLayerVisibility(page, "Stations", false);
        await setLayerVisibility(page, "Anomalies", false);
        await setLayerVisibility(page, "Spot Density", true);

        await page
            .getByRole("radio", {
                name: "Full motion",
            })
            .check();

        await expect(
            page.getByRole("radio", {
                name: "Full motion",
            }),
        ).toBeChecked();

        const firstFrame = await globe.screenshot();

        await page.waitForTimeout(250);

        const secondFrame = await globe.screenshot();

        expect(secondFrame.equals(firstFrame)).toBe(false);
    });
});
