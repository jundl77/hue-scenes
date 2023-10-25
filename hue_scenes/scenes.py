import asyncio
import random
import datetime
import logging
from typing import Optional
from aiohue import HueBridgeV2
from rgbxy import Converter
from hue_scenes.typedefs import HueLight, RGBColor, HueState


def color_temp_to_mired(kelvin: float) -> int:
    return int(1000000.0 / kelvin)


def select_new_random_color(colors: list[RGBColor], previous_color: RGBColor) -> RGBColor:
    # make sure we don't select the same channel as last time
    new_color: int = random.randrange(0, len(colors), 1)
    while colors[new_color] == previous_color:
        new_color = random.randrange(0, len(colors), 1)
    return colors[new_color]


class LightScene:
    def __init__(self,
                 name: str,
                 bridge: HueBridgeV2,
                 converter: Converter,
                 lights: list[HueLight],
                 color_palette: list[RGBColor],
                 start_delay_sec: float,
                 update_interval_sec: float,
                 change_all_lights_together: bool,
                 transition_time_100ms: Optional[int],
                 flash_interval_sec: Optional[float]):
        # params
        self.name: str = name
        self.bridge: HueBridgeV2 = bridge
        self.lights: list[HueLight] = lights
        self.converter: Converter = converter
        self.color_palette: list[RGBColor] = color_palette
        assert len(self.color_palette) > 1, 'at least two colors are needed in the color palette'
        self.rgb_color: RGBColor = self.color_palette[0]
        self.start_delay_sec: float = start_delay_sec
        self.update_interval_sec: float = update_interval_sec
        self.change_all_lights_together: bool = change_all_lights_together
        self.transition_time_100ms: Optional[int] = transition_time_100ms
        if flash_interval_sec is not None:
            self.flash_interval: Optional[datetime.timedelta] = datetime.timedelta(seconds=flash_interval_sec)
        else:
            self.flash_interval: Optional[datetime.timedelta] = None

        # state
        self.last_flash_ts: datetime.datetime = datetime.datetime.now() - datetime.timedelta(self.start_delay_sec)

    async def run(self):
        await asyncio.sleep(self.start_delay_sec)

        logging.info(f"[{self.name}] starting scene..")
        while True:
            await self._update_lights()
            await asyncio.sleep(self.update_interval_sec)

    async def _update_lights(self):
        now = datetime.datetime.now()
        state: HueState = self._compute_new_state()

        coros = list()
        for light in self.lights:
            if not self.change_all_lights_together:
                state: HueState = self._compute_new_state()
            logging.debug(f"[{self.name}] updating lights to: brightness={state.brightness}, rgb={self.rgb_color}")
            should_flash: bool = random.random() > 0.5
            if self.flash_interval is not None and now - self.last_flash_ts > self.flash_interval and should_flash:
                coros.append(self.bridge.lights.set_state(id=light.id, on=True, brightness=state.brightness,
                                                          color_xy=state.color_xy, color_temp=state.color_temp,
                                                          transition_time=30))
                logging.info(f"[{self.name}] {light.metadata.name} flashed")
            else:
                coros.append(self.bridge.lights.set_state(id=light.id, on=True, brightness=state.brightness,
                                                          color_xy=state.color_xy,
                                                          transition_time=self.transition_time_100ms))

        if self.flash_interval is not None and now - self.last_flash_ts > self.flash_interval:
            self.last_flash_ts = now

        try:
            await asyncio.gather(*coros)
        except Exception as e:
            logging.error(f"[{self.name}] encountered error updating lights, are the lights off? - error={e}")

    def _compute_new_state(self) -> HueState:
        brightness = int(random.betavariate(10, 2) * 100)
        self.rgb_color = select_new_random_color(self.color_palette, self.rgb_color)
        color_xy = self.converter.rgb_to_xy(self.rgb_color.r, self.rgb_color.g, self.rgb_color.b)
        color_temp_kelvin = int(random.betavariate(10, 35) * 10000)
        color_temp = color_temp_to_mired(max(min(color_temp_kelvin, 1000), 3000))
        return HueState(brightness=brightness, color_xy=color_xy, color_temp=color_temp)
