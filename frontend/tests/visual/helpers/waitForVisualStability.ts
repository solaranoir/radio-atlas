import type { Locator } from "@playwright/test";

export async function waitForVisualStability(locator: Locator): Promise<void> {
    let previousScreenshot = await locator.screenshot();

    for (let attempt = 0; attempt < 10; attempt += 1) {
        await locator.page().waitForTimeout(100);

        const currentScreenshot = await locator.screenshot();

        if (currentScreenshot.equals(previousScreenshot)) {
            return;
        }

        previousScreenshot = currentScreenshot;
    }

    throw new Error("Globe did not reach a stable visual state");
}
