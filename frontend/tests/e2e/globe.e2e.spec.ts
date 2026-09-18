import { expect, type Page, test } from "@playwright/test";

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

function projectGeographicCoordinates(
    latitude: number,
    longitude: number,
    width: number,
    height: number,
): { x: number; y: number } {
    const degreesToRadians = Math.PI / 180;

    const latitudeRadians = latitude * degreesToRadians;
    const longitudeRadians = longitude * degreesToRadians;

    const radius = 1.01;

    const worldX =
        radius * Math.cos(latitudeRadians) * Math.cos(longitudeRadians);

    const worldY = radius * Math.sin(latitudeRadians);

    const worldZ =
        -radius * Math.cos(latitudeRadians) * Math.sin(longitudeRadians);

    const cameraZ = 2.6;
    const depth = cameraZ - worldZ;

    const verticalFieldOfView = 45 * degreesToRadians;
    const focalScale = 1 / Math.tan(verticalFieldOfView / 2);

    const aspect = width / height;

    const normalizedX = (worldX * focalScale) / (depth * aspect);

    const normalizedY = (worldY * focalScale) / depth;

    return {
        x: ((normalizedX + 1) / 2) * width,
        y: ((1 - normalizedY) / 2) * height,
    };
}

test.describe("Radio Weather Globe", () => {
    test.beforeEach(async ({ page }) => {
        await mockObservations(page);

        await page.goto("/");

        await expect(
            page.getByRole("application", {
                name: "Interactive radio weather globe",
            }),
        ).toBeVisible();
    });

    test("persists layer visibility changes", async ({ page }) => {
        const signalPaths = page.getByRole("checkbox", {
            name: "Signal Paths",
        });

        await expect(signalPaths).toBeChecked();

        await signalPaths.uncheck();

        await expect(signalPaths).not.toBeChecked();

        await page.reload();

        await expect(signalPaths).not.toBeChecked();

        await signalPaths.check();

        await expect(signalPaths).toBeChecked();

        await page.reload();

        await expect(signalPaths).toBeChecked();
    });

    test("filters observations and resets the filters", async ({ page }) => {
        const informationPanel = page.getByText("Information").locator("..");

        const observationCount = informationPanel
            .getByText("Observations")
            .locator("..")
            .locator("dd");

        await expect(observationCount).toHaveText("3");

        const bandFilter = page.getByLabel("Band");
        const modeFilter = page.getByLabel("Mode");

        await bandFilter.selectOption("20m");

        await expect(bandFilter).toHaveValue("20m");
        await expect(observationCount).toHaveText("2");

        await modeFilter.selectOption("FT8");

        await expect(modeFilter).toHaveValue("FT8");
        await expect(observationCount).toHaveText("1");

        await page
            .getByRole("button", {
                name: "Reset filters",
            })
            .click();

        await expect(bandFilter).toHaveValue("");
        await expect(modeFilter).toHaveValue("");
        await expect(observationCount).toHaveText("3");
    });

    test("selects and clears a station on the globe", async ({ page }) => {
        const globe = page.getByRole("application", {
            name: "Interactive radio weather globe",
        });

        const emptySelection = page.getByText(
            "Select a station or signal path to view details.",
        );

        await expect(emptySelection).toBeVisible();

        const canvas = globe.locator("canvas");

        await expect(canvas).toBeVisible();

        const bounds = await canvas.boundingBox();

        expect(bounds).not.toBeNull();

        if (!bounds) {
            throw new Error("Globe canvas has no bounding box");
        }

        const quito = projectGeographicCoordinates(
            -0.1807,
            -78.4678,
            bounds.width,
            bounds.height,
        );

        await canvas.click({
            position: quito,
        });

        await expect(
            page.getByRole("heading", {
                name: "QUITO",
            }),
        ).toBeVisible();

        await expect(emptySelection).not.toBeVisible();

        await globe.focus();
        await page.keyboard.press("Escape");

        await expect(emptySelection).toBeVisible();

        await expect(
            page.getByRole("heading", {
                name: "QUITO",
            }),
        ).not.toBeVisible();
    });
    test("rotates and resets the globe camera", async ({ page }) => {
        const globe = page.getByRole("application", {
            name: "Interactive radio weather globe",
        });

        const canvas = globe.locator("canvas");

        await expect(canvas).toBeVisible();

        const bounds = await canvas.boundingBox();

        expect(bounds).not.toBeNull();

        if (!bounds) {
            throw new Error("Globe canvas has no bounding box");
        }

        const quito = projectGeographicCoordinates(
            -0.1807,
            -78.4678,
            bounds.width,
            bounds.height,
        );

        await globe.focus();

        for (let step = 0; step < 6; step += 1) {
            await page.keyboard.press("ArrowRight");
        }

        await canvas.click({
            position: quito,
        });

        await expect(
            page.getByRole("heading", {
                name: "QUITO",
            }),
        ).not.toBeVisible();

        await page
            .getByRole("button", {
                name: "Reset camera",
            })
            .click();

        await canvas.click({
            position: quito,
        });

        await expect(
            page.getByRole("heading", {
                name: "QUITO",
            }),
        ).toBeVisible();
    });
});
