from disco.bot import Plugin
from disco.types.message import MessageEmbed
from weather.weather import Weather, WeatherObject
from weather.objects.unit_obj import Unit
from weather.objects.wind_obj import Wind


class WeatherPlugin(Plugin):
    CARDINAL_DIRS = (
        'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW',
        'WSW', 'W', 'WNW', 'NW', 'NNW')
    PRESSURE_STATES = ('steady', 'rising', 'falling')
    ICONS = (
        '50d', '11d', '50d', '11d', '11d', '13d', '13d', '13d', '09d', '09d',
        '09d', '09d', '09d', '13d', '13d', '13d', '13d', '09d', '13d', '50d',
        '50d', '50d', '50d', '50d', '50d', '13d', '03d', '02n', '02d', '02n',
        '02d', '01n', '01d', '01n', '01d', '09d', '01d', '11d', '11d', '11d',
        '09d', '13d', '13d', '13d', '04d', '11d', '13d', '11d')
    ICON_BASE = 'http://openweathermap.org/img/w/'

    def __init__(self, bot, config):
        super().__init__(bot, config)

        self.weather = Weather()

    @Plugin.command('weather', '<location:str...>')
    def weather_command(self, event, location):
        result: WeatherObject = self.weather.lookup_by_location(location)

        if not result:
            event.msg.reply(f'Could not find weather for `{location}`.')
            return

        embed: MessageEmbed = MessageEmbed()
        embed.set_author(name='Yahoo! Weather')
        embed.title = result.title[17:]
        embed.url = result.print_obj['link'].split('*')[-1]
        embed.description = result.condition.text
        embed.add_field(
            name='Temperature',
            value=f'{result.condition.temp}° {result.units.temperature}',
            inline=True)
        embed.add_field(
            name='Atmosphere',
            value=self.format_atmosphere(result.atmosphere, result.units),
            inline=True)
        embed.add_field(
            name='Wind',
            value=self.format_wind(result.wind, result.units),
            inline=True)
        embed.add_field(
            name='Astronomy',
            value=self.format_astronomy(result),
            inline=True)

        code = int(result.condition.code)

        if code != 3200:
            embed.set_thumbnail(url=f'{self.ICON_BASE}{self.ICONS[code]}.png')

        event.msg.reply(embed=embed)

    @staticmethod
    def format_atmosphere(atm: dict, units: Unit) -> str:
        state: str = WeatherPlugin.PRESSURE_STATES[int(atm['rising'])]

        return f'Humidity: {atm["humidity"]}%\n' \
               f'Pressure: {atm["pressure"]} {units.pressure} ({state})\n' \
               f'Visibility: {atm["visibility"]} {units.distance}'

    @staticmethod
    def format_wind(wind: Wind, units: Unit) -> str:
        degrees: str = wind.direction
        cardinal: str = WeatherPlugin.get_cardinal_dir(degrees)

        return f'{degrees}° ({cardinal}) at {wind.speed} ' \
               f'{units.speed}\nWind chill: {wind.chill}'

    @staticmethod
    def format_astronomy(result: WeatherObject) -> str:
        tz: str = result.last_build_date[-3:]
        ast: dict = result.astronomy

        return f'Sunrise: {ast["sunrise"]} {tz}\nSunset: {ast["sunset"]} {tz}'

    @staticmethod
    def get_cardinal_dir(degrees: str) -> str:
        return WeatherPlugin.CARDINAL_DIRS[int((int(degrees) / 22.5) + 0.5)]
