from typing import Any, cast

from fastapi.testclient import TestClient

from app.main import create_app


def _schema() -> dict[str, Any]:
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200

    return cast(dict[str, Any], response.json())


def test_openapi_metadata_has_correct_title_and_version() -> None:
    schema = _schema()

    info = schema["info"]

    assert info["title"] == "SolaraSphere: Radio Atlas API"
    assert info["version"] == "0.1.0"


def test_observations_endpoint_exists_in_schema() -> None:
    schema = _schema()

    paths = schema["paths"]

    assert "/api/v1/observations" in paths
    assert "get" in paths["/api/v1/observations"]


def test_solar_conditions_endpoint_exists_in_schema() -> None:
    schema = _schema()

    paths = schema["paths"]

    assert "/api/v1/solar-conditions" in paths
    assert "get" in paths["/api/v1/solar-conditions"]


def test_stations_endpoint_exists_in_schema() -> None:
    schema = _schema()

    paths = schema["paths"]

    assert "/api/v1/stations" in paths
    assert "get" in paths["/api/v1/stations"]


def test_endpoint_summaries_and_descriptions_are_present() -> None:
    schema = _schema()

    paths = schema["paths"]

    observations = paths["/api/v1/observations"]["get"]
    solar_conditions = paths["/api/v1/solar-conditions"]["get"]
    stations = paths["/api/v1/stations"]["get"]

    assert observations["summary"] == "List radio observations"
    assert observations["description"]

    assert solar_conditions["summary"] == "List solar conditions"
    assert solar_conditions["description"]

    assert stations["summary"] == "List amateur radio stations"
    assert stations["description"]


def test_observation_response_schema_is_referenced() -> None:
    schema = _schema()

    response_schema = schema["paths"]["/api/v1/observations"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    items = response_schema["items"]

    assert items["$ref"].endswith("/ObservationResponse")


def test_solar_condition_response_schema_is_referenced() -> None:
    schema = _schema()

    response_schema = schema["paths"]["/api/v1/solar-conditions"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]

    items = response_schema["items"]

    assert items["$ref"].endswith("/SolarConditionResponse")


def test_station_response_schema_is_referenced() -> None:
    schema = _schema()

    response_schema = schema["paths"]["/api/v1/stations"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    items = response_schema["items"]

    assert items["$ref"].endswith("/StationResponse")


def test_standardized_error_responses_are_documented() -> None:
    schema = _schema()

    paths = schema["paths"]

    observations_responses = paths["/api/v1/observations"]["get"]["responses"]

    solar_responses = paths["/api/v1/solar-conditions"]["get"]["responses"]

    station_responses = paths["/api/v1/stations"]["get"]["responses"]

    for responses in (
        observations_responses,
        solar_responses,
    ):
        assert "400" in responses
        assert "422" in responses
        assert "500" in responses

    assert "422" in station_responses
    assert "500" in station_responses


def test_example_payloads_appear_in_generated_schema() -> None:
    schema = _schema()

    schemas = schema["components"]["schemas"]

    observation_example = schemas["ObservationResponse"]["example"]

    solar_example = schemas["SolarConditionResponse"]["example"]

    station_example = schemas["StationResponse"]["example"]

    assert observation_example["sender_callsign"]
    assert observation_example["receiver_callsign"]

    assert solar_example["observation_type"]
    assert "data" in solar_example

    assert station_example["callsign"]
    assert "grid_square" in station_example


def test_query_parameters_are_documented() -> None:
    schema = _schema()

    paths = schema["paths"]

    observations_parameters = {
        parameter["name"] for parameter in paths["/api/v1/observations"]["get"]["parameters"]
    }

    solar_parameters = {
        parameter["name"] for parameter in paths["/api/v1/solar-conditions"]["get"]["parameters"]
    }

    station_parameters = {
        parameter["name"] for parameter in paths["/api/v1/stations"]["get"]["parameters"]
    }

    assert {
        "band",
        "start_time",
        "end_time",
        "limit",
        "offset",
    } <= observations_parameters

    assert {
        "observation_type",
        "start_time",
        "end_time",
        "limit",
        "offset",
    } <= solar_parameters

    assert {
        "callsign",
        "limit",
        "offset",
    } <= station_parameters


def test_observations_query_parameters_have_examples() -> None:
    schema = _schema()

    parameters = schema["paths"]["/api/v1/observations"]["get"]["parameters"]

    examples = {
        parameter["name"]: parameter["schema"].get("examples") or parameter.get("examples")
        for parameter in parameters
    }

    assert examples["start_time"]
    assert examples["end_time"]
    assert examples["band"]
    assert examples["limit"]
    assert examples["offset"]


def test_solar_query_parameters_have_examples() -> None:
    schema = _schema()

    parameters = schema["paths"]["/api/v1/solar-conditions"]["get"]["parameters"]

    examples = {
        parameter["name"]: parameter["schema"].get("examples") or parameter.get("examples")
        for parameter in parameters
    }

    assert examples["observation_type"]
    assert examples["start_time"]
    assert examples["end_time"]
    assert examples["limit"]
    assert examples["offset"]


def test_station_query_parameters_have_examples() -> None:
    schema = _schema()

    parameters = schema["paths"]["/api/v1/stations"]["get"]["parameters"]

    examples = {
        parameter["name"]: parameter["schema"].get("examples") or parameter.get("examples")
        for parameter in parameters
    }

    assert examples["callsign"]
    assert examples["limit"]
    assert examples["offset"]


def test_400_error_example_is_documented() -> None:
    schema = _schema()

    response = schema["paths"]["/api/v1/observations"]["get"]["responses"]["400"]

    example = response["content"]["application/json"]["example"]

    assert example == {
        "error": {
            "code": "invalid_time_range",
            "message": "start_time must be before or equal to end_time",
        }
    }


def test_422_error_example_is_documented() -> None:
    schema = _schema()

    response = schema["paths"]["/api/v1/observations"]["get"]["responses"]["422"]

    example = response["content"]["application/json"]["example"]

    assert example["error"]["code"] == "validation_error"
    assert example["error"]["message"] == "Request validation failed"
    assert example["error"]["details"]


def test_500_error_example_is_documented() -> None:
    schema = _schema()

    response = schema["paths"]["/api/v1/observations"]["get"]["responses"]["500"]

    example = response["content"]["application/json"]["example"]

    assert example == {
        "error": {
            "code": "response_validation_error",
            "message": "Response validation failed",
        }
    }
