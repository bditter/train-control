"""Select entities for RailOps."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import DccExClient, TrainConfig
from .const import DATA_CLIENT, DOMAIN, OPT_TRAINS
from .entity import RailOpsTrainEntity

FORWARD = "Forward"
REVERSE = "Reverse"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RailOps select entities."""
    client: DccExClient = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
    async_add_entities(
        RailOpsDirectionSelect(entry, client, TrainConfig.from_dict(train))
        for train in entry.options.get(OPT_TRAINS, [])
    )


class RailOpsDirectionSelect(RailOpsTrainEntity, SelectEntity):
    """Train direction control."""

    _attr_icon = "mdi:swap-horizontal"
    _attr_options = [FORWARD, REVERSE]

    def __init__(
        self, entry: ConfigEntry, client: DccExClient, train: TrainConfig
    ) -> None:
        """Initialize the direction select."""
        super().__init__(entry, client, train)
        self._attr_unique_id = f"train_{entry.entry_id}_{train.train_id}_direction"
        self._attr_name = "Direction"
        self._unsub: Callable[[], None] | None = None

    @property
    def current_option(self) -> str:
        """Return current direction."""
        return FORWARD if self._client.get_forward(self._train.address) else REVERSE

    async def async_select_option(self, option: str) -> None:
        """Set train direction."""
        await self._client.async_set_direction(self._train, option == FORWARD)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to train updates."""
        self._unsub = self._client.subscribe_train(
            self._train.address, self._train_updated
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from train updates."""
        if self._unsub:
            self._unsub()

    @callback
    def _train_updated(self, data: dict) -> None:
        """Refresh state after a train broadcast."""
        self.async_write_ha_state()
