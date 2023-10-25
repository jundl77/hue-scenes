#!/usr/bin/python

import asyncio
import logging
import json
from typing import Optional
from pathlib import Path
from aiohue import HueBridgeV2, create_app_key
from aiohue.discovery import discover_nupnp
from rgbxy import Converter, GamutA, GamutB, GamutC
from hue_scenes.scenes import LightScene
from hue_scenes.typedefs import HueLight, RGBColor

logging.basicConfig(format='%(asctime)s [%(levelname)s ] %(message)s', level=logging.INFO)

HUE_API_KEY_PATH = '~/.aiohue_api_key.json'
HOST_IP = '192.168.178.22'


async def find_bridge_host() -> str:
    discovered_bridges = await discover_nupnp()
    assert len(discovered_bridges) == 1, f"needs to find exactly one bridge, but found {len(discovered_bridges)}"
    return discovered_bridges[0].host


async def authenticate_bridge(host: str) -> Optional[str]:
    logging.info(f"No existing api_key found, creating new api_key for bridge: {host}")
    input("Press the link button on the bridge and press enter to continue...")

    try:
        api_key = await create_app_key(host, "authentication_example")
        logging.info(f"Authentication succeeded, api key: {api_key}")
        save_api_key(api_key)
        return api_key
    except Exception as exc:
        logging.error("ERROR: ", str(exc))
        return None


def save_api_key(api_key: str):
    json_string = {
        'api_key': api_key
    }
    path = Path(HUE_API_KEY_PATH).expanduser().absolute()
    with open(str(path), 'w') as f:
        json.dump(json_string, f)


def load_api_key() -> Optional[str]:
    path = Path(HUE_API_KEY_PATH).expanduser().absolute()
    if not path.exists():
        return None

    with open(str(path), 'r') as f:
        data = json.load(f)
        return data['api_key']


def find_lights(bridge: HueBridgeV2, light_names: list[str]) -> list[HueLight]:
    lights: list[HueLight] = list()
    for light in bridge.lights:
        if light.metadata.name in light_names:
            lights.append(light)
    return lights


async def main():
    if HOST_IP is None:
        host = await find_bridge_host()
    else:
        host = HOST_IP
    api_key = load_api_key()
    if api_key is None:
        api_key = await authenticate_bridge(host)
        if api_key is None:
            logging.error("unable to get api ky, quitting.")
            return

    async with HueBridgeV2(host, api_key) as bridge:
        logging.info(f"connected to bridge: {bridge.bridge_id}")
        logging.info(bridge.config.bridge_device)

        logging.info(f"found lights: {[l.metadata.name for l in bridge.lights]}")
        logging.info(f"found devices: {[d.metadata.name for d in bridge.devices]}")

        converter: Converter = Converter(GamutA)

        # horror scene
        horror_lights = find_lights(bridge, ['Lvrm Cndl 1', 'Lvrm Cndl 2', 'Lvrm Cndl 3',  'Lvrm Cndl 4', 'Lvrm Cndl 5', 'Lvrm Lmp 1'])
        horror_color_palette: list[RGBColor] = [RGBColor(255, 0, 0), RGBColor(254, 0, 0)]
        horror_scene: LightScene = LightScene(name='horror',
                                              bridge=bridge,
                                              converter=converter,
                                              lights=horror_lights,
                                              color_palette=horror_color_palette,
                                              start_delay_sec=0,
                                              update_interval_sec=0.5,
                                              change_all_lights_together=False,
                                              transition_time_100ms=1000,
                                              flash_interval_sec=65)

        # spider scene
        spider_lights = find_lights(bridge, ['Hlwy 1', 'Hlwy 2', 'Hlwy 3',  'Hlwy 4', 'Hlwy 5', 'Hlwy 6'])
        spider_color_palette: list[RGBColor] = [RGBColor(0, 102, 255), RGBColor(0, 153, 255), RGBColor(0, 0, 255)]
        spider_scene: LightScene = LightScene(name='spider',
                                              bridge=bridge,
                                              converter=converter,
                                              lights=spider_lights,
                                              color_palette=spider_color_palette,
                                              start_delay_sec=20,
                                              update_interval_sec=0.5,
                                              change_all_lights_together=False,
                                              transition_time_100ms=1000,
                                              flash_interval_sec=60)

        # graveyard scene
        graveyard_lights = find_lights(bridge, ['O1', 'O2', 'O3'])
        graveyard_color_palette: list[RGBColor] = [RGBColor(204, 255, 204), RGBColor(153, 255, 204), RGBColor(153, 255, 153), RGBColor(204, 255, 153),
                                                   RGBColor(102, 255, 153), RGBColor(51, 204, 51), RGBColor(153, 255, 102)]
        graveyard_scene: LightScene = LightScene(name='graveyard',
                                                 bridge=bridge,
                                                 converter=converter,
                                                 lights=graveyard_lights,
                                                 color_palette=graveyard_color_palette,
                                                 start_delay_sec=40,
                                                 update_interval_sec=1,
                                                 change_all_lights_together=False,
                                                 transition_time_100ms=50000,
                                                 flash_interval_sec=55)

        # potions scene
        potions_lights = find_lights(bridge, ['Kt 1', 'Kt 2', 'Kt 3'])
        potions_color_palette: list[RGBColor] = [
            RGBColor(255, 0, 0), RGBColor(0, 255, 0), RGBColor(0, 0, 255), RGBColor(255, 255, 0), RGBColor(0, 255, 255), RGBColor(255, 0, 255)
        ]
        potions_scene: LightScene = LightScene(name='potions',
                                               bridge=bridge,
                                               converter=converter,
                                               lights=potions_lights,
                                               color_palette=potions_color_palette,
                                               start_delay_sec=0,
                                               update_interval_sec=10,
                                               change_all_lights_together=True,
                                               transition_time_100ms=10000,
                                               flash_interval_sec=None)

        coros = [horror_scene.run(), spider_scene.run(), graveyard_scene.run(), potions_scene.run()]
        await asyncio.gather(*coros)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
