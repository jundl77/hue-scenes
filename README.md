# hue_scenes

A very simple script to build custom Philips Hue lighting animations / scenes. I used this for Halloween themed animations.

To use this, create your custom animations / scenes by looking at main.py.


### Features
The following features are currently supported:

- iterate through a set of colors, with a configurable transition period and interval
- brightness of scenes adjusts on each iteration, creating a flickering effect
- create flashes on a specified interval

Example of a scene:
```
# horror scene
horror_lights = find_lights(bridge, ['Hlwy 1', 'Hlwy 2', 'Hlwy 3',  'Hlwy 4', 'Hlwy 5', 'Hlwy 6'])
horror_color_palette: list[RGBColor] = [RGBColor(255, 0, 0), RGBColor(254, 0, 0)]
horror_scene: LightScene = LightScene(name='horror',
                                      bridge=bridge,
                                      converter=converter,
                                      lights=horror_lights,
                                      color_palette=horror_color_palette,
                                      start_delay_sec=0,
                                      update_interval_sec=0.5,
                                      change_all_lights_together=False,
                                      transition_time_100ms=None,
                                      flash_interval_sec=60)
```
This scene will stay red, flicker a little bit (brightness is adjusted every 0.5sec), and flash every 60sec.