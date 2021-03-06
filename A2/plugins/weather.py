"""Functions related to weather."""
from datetime import datetime
import re

from disco.bot import Config, Plugin
from disco.types.message import MessageEmbed
from weather import Unit
from weather.weather import Weather


class WeatherConfig(Config):
    default_unit = Unit.CELSIUS


@Plugin.with_config(WeatherConfig)
class WeatherPlugin(Plugin):
    CARDINAL_DIRS = (
        'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW',
        'WSW', 'W', 'WNW', 'NW', 'NNW')
    PRESSURE_STATES = ('steady', 'rising', 'falling')
    UNIT_CHOICES = ('c', 'f')
    TIME_FORMATS = {'c': '%H:%M', 'f': '%I:%M %p'}
    TITLE_PATTERN = re.compile(
        r'Conditions for (.+?) at ((\d+):(\d+) ([AP]M)) (.+)', re.IGNORECASE)

    # Maps Yahoo's condition codes to OpenWeatherMap's weather icons and emojis.
    ICONS = (
        ('50d', '🌪️'), ('11d', '⛈️'), ('50d', '🌀'), ('11d', '⛈️'),
        ('11d', '🌩️'), ('13d', '🌨️'), ('13d', '🌨️'), ('13d', '🌨️'),
        ('09d', '💧'), ('09d', '💧'), ('09d', '🌧️'), ('09d', '🌧️'),
        ('09d', '🌧️'), ('13d', '🌨️'), ('13d', '🌨️'), ('13d', '🌨️'),
        ('13d', '🌨️'), ('09d', '🌧️'), ('13d', '🌨️'), ('50d', '💨'),
        ('50d', '🌫️'), ('50d', '🌫️'), ('50d', '💨'), ('50d', '💨'),
        ('50d', '💨'), ('13d', '❄️'), ('03d', '☁️'), ('02n', '☁️'),
        ('02d', '🌥️'), ('02n', '☁️'), ('02d', '⛅'), ('01n', '🌙'),
        ('01d', '☀️'), ('01n', '🌙'), ('01d', '🌤️'), ('09d', '🌧️'),
        ('01d', '♨️'), ('11d', '🌩️'), ('11d', '🌩️'), ('11d', '🌩️'),
        ('09d', '🌦️'), ('13d', '🌨️'), ('13d', '🌨️'), ('13d', '🌨️'),
        ('04d', '☁️'), ('11d', '🌩️'), ('13d', '🌨️'), ('11d', '🌩️'))

    def load(self, ctx):
        super().load(ctx)

        self.config.default_unit = self.config.default_unit.lower()
        assert self.config.default_unit in self.UNIT_CHOICES, \
            "Invalid default unit: {}".format(self.config.default_unit)

        self.weather = Weather(self.config.default_unit)

    @Plugin.command('weather', parser=True)
    @Plugin.parser.add_argument('location', nargs='+', type=str)
    @Plugin.parser.add_argument(
        '-u', '--unit', type=str.lower, choices=UNIT_CHOICES)
    def weather_command(self, event, args):
        """= weather =
        Displays the weather for a given location.
        Provides information on temperature, atmosphere, wind, & astronomy.
        usage       :: $weather <location> [-u]
        aliases     :: None
        category    :: Weather
        == Arguments
        location    :: The location for which to look up the weather.
        == Flags
        -u/--unit   :: The unit of measurement in which to display temperature.
        == Examples
        $weather new york `Displays the weather for New York city.`
        $weather singapore, sg -u f `Displays the weather for Singapore in Fahrenheit.`
        $weather --unit c berlin `Displays the weather for Berlin in Celsius.`
        """
        args.location = ' '.join(args.location)
        self.weather.unit = args.unit if args.unit else self.config.default_unit
        result = self.weather.lookup_by_location(args.location)

        # Sometimes the response is OK but only contains units. Assumes failure
        # if some arbitrary top-level element besides units doesn't exist.
        if not result or 'link' not in result.print_obj:
            event.msg.reply(
                'Could not find weather for `{}`.'.format(args.location))
            return

        title, tz = self.format_condition_title(
            result.print_obj['item']['title'], result.units.temperature)

        embed = self.get_base_embed(result)
        embed.title = title
        embed.set_thumbnail(url=self.get_thumbnail(result.condition.code))
        embed.description = self.format_condition(result)
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
            value=self.format_astronomy(result, tz),
            inline=True)

        event.msg.reply(embed=embed)

    @Plugin.command('forecast', parser=True)
    @Plugin.parser.add_argument('location', nargs='+', type=str)
    @Plugin.parser.add_argument(
        '-u', '--unit', type=str.lower, choices=UNIT_CHOICES)
    def forecast_command(self, event, args):
        """= forecast =
        Displays a 10-day weather forecast for a given location.
        usage       :: $forecast <location> [-u]
        aliases     :: None
        category    :: Weather
        == Arguments
        location    :: The location for which to retrieve a forecast.
        == Flags
        -u/--unit   :: The unit of measurement in which to display temperature.
        == Examples
        $forecast new york `Displays the forecast for New York city.`
        $forecast singapore, sg -u f `Displays the forecast for Singapore in Fahrenheit.`
        $forecast --unit c berlin `Displays the forecast for Berlin in Celsius.`
        """
        args.location = ' '.join(args.location)
        self.weather.unit = args.unit if args.unit else self.config.default_unit
        result = self.weather.lookup_by_location(args.location)

        # Sometimes the response is OK but only contains units. Assumes failure
        # if some arbitrary top-level element besides units doesn't exist.
        if not result or 'link' not in result.print_obj:
            event.msg.reply(
                'Could not retrieve a forecast for `{}`.'.format(args.location))
            return

        embed = self.get_base_embed(result)
        embed.title = '10-day Weather Forecast for {}'.format(result.title[17:])

        for forecast in result.forecast:
            emoji = WeatherPlugin.get_emoji(forecast.code)

            embed.add_field(
                name='{} ({})'.format(forecast.day, forecast.date[:6]),
                value='{}{}\nHigh: `{}° {}`\nLow: `{}° {}`'.format(
                    emoji, forecast.text, forecast.high,
                    result.units.temperature, forecast.low,
                    result.units.temperature),
                inline=True)

        event.msg.reply(embed=embed)

    @staticmethod
    def get_base_embed(result):
        """Creates an embed and sets some common properties."""
        embed = MessageEmbed()
        embed.set_author(
            name='Yahoo! Weather',
            url='https://www.yahoo.com/news/weather',
            icon_url='https://s.yimg.com/dh/ap/default/130909/y_200_a.png')
        embed.url = result.print_obj['link'].split('*')[-1]  # Removes RSS URL.
        embed.color = 4194448  # Yahoo! logo's purple.

        return embed

    @staticmethod
    def format_condition_title(title, unit):
        """Formats the time of a condition's title.

        Returns the formatted title and parsed the timezone.
        """
        match = WeatherPlugin.TITLE_PATTERN.fullmatch(title)
        time = WeatherPlugin.format_time(match.group(2), unit)
        tz = match.group(6)
        title = "Conditions for {} at {} {}".format(match.group(1), time, tz)

        return title, tz

    @staticmethod
    def format_condition(result):
        """Formats a string displaying the current condition information."""
        forecast = result.forecast[0]
        emoji = WeatherPlugin.get_emoji(result.condition.code)

        temp = result.condition.temp
        unit = result.units.temperature
        alt_temp = WeatherPlugin.convert_temp(result.condition.temp, unit)
        alt_unit = next(
            u.upper() for u in WeatherPlugin.UNIT_CHOICES if u.upper() != unit)

        condition = '{}{}° {} - {} ({}° {})\n'.format(
            emoji, temp, unit, result.condition.text, alt_temp, alt_unit)

        forecasts = 'High: `{0}° {2}`\nLow: `{1}° {2}`'.format(
            forecast.high, forecast.low, unit)

        return condition + forecasts

    @staticmethod
    def format_atmosphere(atm, units):
        """Formats a string to displays atmosphere information."""
        state = WeatherPlugin.PRESSURE_STATES[int(atm['rising'])]

        return 'Humidity: `{}%`\nPressure: `{} {}` ({})\nVisibility: `{} {}`'\
            .format(atm["humidity"], atm["pressure"], units.pressure, state,
                    atm["visibility"], units.distance)

    @staticmethod
    def format_wind(wind, units):
        """Formats a string to displays wind information."""
        degrees = wind.direction
        cardinal = WeatherPlugin.get_cardinal_dir(degrees)

        return '`{}°` ({}) at `{} {}`\nWind chill: `{}`'.format(
            degrees, cardinal, wind.speed, units.speed, wind.chill)

    @staticmethod
    def format_astronomy(result, tz):
        """Formats a string to displays astronomy information."""
        unit = result.units.temperature
        sunrise = WeatherPlugin.format_time(result.astronomy["sunrise"], unit)
        sunset = WeatherPlugin.format_time(result.astronomy["sunset"], unit)

        return 'Sunrise: `{0} {2}`\nSunset: `{1} {2}`'.format(
            sunrise, sunset, tz)

    @staticmethod
    def get_cardinal_dir(degrees):
        """Converts degrees to an abbreviated cardinal direction."""
        index = int((int(degrees) % 360 / 22.5) + 0.5)

        return WeatherPlugin.CARDINAL_DIRS[index]

    @staticmethod
    def get_emoji(code):
        """Returns an emoji based on a condition code."""
        code = int(code)

        return WeatherPlugin.ICONS[code][1] + ' ' if code != 3200 else ''

    @staticmethod
    def get_thumbnail(code):
        """Returns an OpenWeatherMap icon URL based on a condition code."""
        code = int(code)

        if code != 3200:
            icon = WeatherPlugin.ICONS[code][0]

            return 'http://openweathermap.org/img/w/{}.png'.format(icon)

    @staticmethod
    def format_time(in_time, unit):
        """Formats time as 12/24 hour based on unit."""
        in_time = re.sub(r'^0:', '12:', in_time, 1)
        out_time = datetime.strptime(in_time, '%I:%M %p')

        return out_time.strftime(WeatherPlugin.TIME_FORMATS[unit.lower()])

    @staticmethod
    def convert_temp(temp, in_unit):
        """Converts a temperature value to a given unit.

        Converted temperature is rounded to 1 decimal place.
        """
        temp = int(temp)
        in_unit = in_unit.lower()

        if in_unit == Unit.FAHRENHEIT:
            return round((temp - 32) * 5.0 / 9.0, 1)
        elif in_unit == Unit.CELSIUS:
            return round(9.0 / 5.0 * temp + 32, 1)

        raise ValueError("Invalid output temperature unit: {}".format(in_unit))
