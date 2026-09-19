import { describe, expect, it } from "vitest";

import type { Station } from "../types/station";
import { StationCollection } from "./StationCollection";

const stationOne: Station = {
    id: "station-one",
    callsign: "KK7QEA",
    latitude: 36.1699,
    longitude: -115.1398,
};

const stationTwo: Station = {
    id: "station-two",
    callsign: "W1AW",
    latitude: 40.7128,
    longitude: -74.006,
};

describe("StationCollection", () => {
    it("adds multiple stations", () => {
        const collection = new StationCollection();

        collection.setStations([stationOne, stationTwo]);

        expect(collection.group.children).toHaveLength(2);

        collection.dispose();
    });

    it("updates an existing station without adding another marker", () => {
        const collection = new StationCollection();

        collection.setStations([stationOne]);

        const updatedStation: Station = {
            ...stationOne,
            callsign: "KK7QEA/P",
            latitude: 37.0,
            longitude: -116.0,
        };

        collection.setStations([updatedStation]);

        expect(collection.group.children).toHaveLength(1);

        expect(collection.group.children[0]?.userData.station).toEqual(
            updatedStation,
        );

        collection.dispose();
    });

    it("removes stations that are no longer present", () => {
        const collection = new StationCollection();

        collection.setStations([stationOne, stationTwo]);

        collection.setStations([stationTwo]);

        expect(collection.group.children).toHaveLength(1);

        expect(collection.group.children[0]?.userData.station).toEqual(
            stationTwo,
        );

        collection.dispose();
    });

    it("clears all rendered stations when disposed", () => {
        const collection = new StationCollection();

        collection.setStations([stationOne, stationTwo]);

        collection.dispose();

        expect(collection.group.children).toHaveLength(0);
    });
});
