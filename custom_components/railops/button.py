"""Button entities for RailOps."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import DccExClient, TrainConfig
from .const import DATA_CLIENT, DOMAIN, OPT_TRAINS
from .entity import RailOpsControllerEntity, RailOpsTrainEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RailOps button entities."""
    client: DccExClient = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    entities: list[ButtonEntity] = [
        RailOpsControllerEmergencyStopButton(entry, client)
    ]
    for train_data in entry.options.get(OPT_TRAINS, []):
        train = TrainConfig.from_dict(train_data)
        entities.extend(
            [
                RailOpsTrainStopButton(entry, client, train),
                RailOpsTrainEmergencyStopButton(entry, client, train),
            ]
        )
    async_add_entities(entities)


class RailOpsControllerEmergencyStopButton(RailOpsControllerEntity, ButtonEntity):
    """Global DCC-EX emergency stop button."""

    _attr_icon = "mdi:alert-octagon"

    def __init__(self, entry: ConfigEntry, client: DccExClient) -> None:
        """Initialize the global emergency stop button."""
        super().__init__(entry, client)
        self._attr_unique_id = f"controller_{entry.entry_id}_emergency_stop"
        self._attr_name = "Emergency Stop"

    async def async_press(self) -> None:
        """Send global emergency stop."""
        await self._client.async_emergency_stop()


class RailOpsTrainStopButton(RailOpsTrainEntity, ButtonEntity):
    """Train stop button."""

    _attr_icon = "mdi:stop"

    def __init__(
        self, entry: ConfigEntry, client: DccExClient, train: TrainConfig
    ) -> None:
        """Initialize the stop button."""
        super().__init__(entry, client, train)
        self._attr_unique_id = f"train_{entry.entry_id}_{train.train_id}_stop"
        self._attr_name = "Stop"

    async def async_press(self) -> None:
        """Stop the train."""
        await self._client.async_stop(self._train)


class RailOpsTrainEmergencyStopButton(RailOpsTrainEntity, ButtonEntity):
    """Train emergency stop button."""

    _attr_icon = "mdi:alert-octagon"

    def __init__(
        self, entry: ConfigEntry, client: DccExClient, train: TrainConfig
    ) -> None:
        """Initialize the emergency stop button."""
        super().__init__(entry, client, train)
        self._attr_unique_id = f"train_{entry.entry_id}_{train.train_id}_emergency_stop"
        self._attr_name = "Emergency Stop"

    async def async_press(self) -> None:
        """Emergency stop the train."""
        await self._client.async_emergency_stop(self._train)
