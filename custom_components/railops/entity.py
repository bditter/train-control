"""Shared RailOps entity helpers."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .client import DccExClient, TrainConfig
from .const import DOMAIN


class RailOpsControllerEntity:
    """Base entity for the DCC-EX command station."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, client: DccExClient) -> None:
        """Initialize the controller entity."""
        self._entry = entry
        self._client = client

    @property
    def device_info(self) -> DeviceInfo:
        """Return controller device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="DCC-EX",
        )


class RailOpsTrainEntity:
    """Base entity for a DCC-EX train address."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: ConfigEntry, client: DccExClient, train: TrainConfig
    ) -> None:
        """Initialize the train entity."""
        self._entry = entry
        self._client = client
        self._train = train

    @property
    def device_info(self) -> DeviceInfo:
        """Return train device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id, self._train.train_id)},
            name=self._train.name,
            manufacturer="DCC-EX",
            via_device=(DOMAIN, self._entry.entry_id),
        )
