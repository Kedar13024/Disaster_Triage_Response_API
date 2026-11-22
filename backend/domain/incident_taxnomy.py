"""Define the supported incident categories and incident types."""

from enum import StrEnum


class IncidentCategory(StrEnum):
    """Broad categories of disaster and emergency incidents."""

    NATURAL_DISASTER = "natural_disaster"
    HUMAN_CAUSED = "human_caused"
    MEDICAL_EMERGENCY = "medical_emergency"
    RESCUE_EMERGENCY = "rescue_emergency"
    PUBLIC_HEALTH = "public_health"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"


class IncidentType(StrEnum):
    """Specific types of incidents supported by the system."""

    # Natural disasters
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    CYCLONE = "cyclone"
    LANDSLIDE = "landslide"
    WILDFIRE = "wildfire"
    DROUGHT = "drought"
    TSUNAMI = "tsunami"
    EXTREME_WEATHER = "extreme_weather"

    # Human-caused incidents
    FIRE = "fire"
    EXPLOSION = "explosion"
    CHEMICAL_HAZARD = "chemical_hazard"
    STRUCTURAL_COLLAPSE = "structural_collapse"
    TRANSPORT_ACCIDENT = "transport_accident"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    CROWD_INCIDENT = "crowd_incident"
    SECURITY_INCIDENT = "security_incident"

    # Medical emergencies
    MEDICAL_EMERGENCY = "medical_emergency"
    MASS_CASUALTY = "mass_casualty"
    TRAUMA = "trauma"

    # Rescue emergencies
    TRAPPED_PERSON = "trapped_person"
    MISSING_PERSON = "missing_person"
    WATER_RESCUE = "water_rescue"
    EVACUATION_REQUIRED = "evacuation_required"

    # Public health
    DISEASE_OUTBREAK = "disease_outbreak"
    CONTAMINATED_WATER = "contaminated_water"
    FOOD_CONTAMINATION = "food_contamination"

    # Infrastructure failures
    POWER_FAILURE = "power_failure"
    WATER_SUPPLY_FAILURE = "water_supply_failure"
    GAS_LEAK = "gas_leak"
    COMMUNICATION_FAILURE = "communication_failure"
    ROAD_DAMAGE = "road_damage"
    BRIDGE_FAILURE = "bridge_failure"