from aiohue.v2.controllers.lights import Light, Type

HueLight = Type[Light]


class RGBColor:
    def __init__(self, r, g, b):
        self.r: int = r
        self.g: int = g
        self.b: int = b

    def __str__(self):
        return f"[r={self.r}, g={self.g}, b={self.b}]"

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b


class HueState:
    def __init__(self, brightness: int, color_xy: tuple[float, float], color_temp: int):
        self.brightness: float = brightness
        self.color_xy: tuple[float, float] = color_xy
        self.color_temp: int = color_temp
