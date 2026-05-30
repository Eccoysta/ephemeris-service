import swisseph as swe
from datetime import datetime
import pytz

# Gezegen sabitleri
PLANETS = [
    (swe.SUN, "Sun"),
    (swe.MOON, "Moon"),
    (swe.MERCURY, "Mercury"),
    (swe.VENUS, "Venus"),
    (swe.MARS, "Mars"),
    (swe.JUPITER, "Jupiter"),
    (swe.SATURN, "Saturn"),
    (swe.URANUS, "Uranus"),
    (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO, "Pluto"),
    (swe.TRUE_NODE, "North Node"),
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Major aspektler
MAJOR_ASPECTS = {
    0:   {"name": "Conjunction", "orb": 8},
    60:  {"name": "Sextile",     "orb": 6},
    90:  {"name": "Square",       "orb": 8},
    120: {"name": "Trine",       "orb": 8},
    180: {"name": "Opposition", "orb": 8},
}

# Minor aspektler
MINOR_ASPECTS = {
    30:  {"name": "Semi-sextile",   "orb": 2},
    45:  {"name": "Semi-square",    "orb": 2},
    135: {"name": "Sesquiquadrate", "orb": 2},
    150: {"name": "Quincunx",       "orb": 3},
    72:  {"name": "Quintile",       "orb": 2},
    144: {"name": "Biquintile",     "orb": 2},
}


def degree_to_sign(degree: float) -> tuple:
    sign_index = int(degree / 30)
    degree_in_sign = degree % 30
    return SIGNS[sign_index], round(degree_in_sign, 2)


def local_to_ut(birth_date: str, birth_time: str, timezone: str) -> float:
    tz = pytz.timezone(timezone)
    dt_str = f"{birth_date} {birth_time}"
    local_dt = tz.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
    utc_dt = local_dt.astimezone(pytz.utc)
    return swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    )


def calculate_planets(jd: float) -> list:
    planets = []
    for planet_id, planet_name in PLANETS:
        # Use default flags (MOOEPH mode for main planets)
        result, serr = swe.calc_ut(jd, planet_id)
        data = result  # data is the first element of the tuple

        longitude = data[0]
        speed = data[3] if len(data) > 3 else 0
        retrograde = speed < 0
        sign, degree = degree_to_sign(longitude)

        planets.append({
            "name": planet_name,
            "longitude": round(longitude, 4),
            "sign": sign,
            "degree": degree,
            "retrograde": retrograde,
        })
    return planets


def calculate_houses(jd: float, lat: float, lng: float) -> tuple:
    cusps, ascmc = swe.houses(jd, lat, lng, b"P")  # Placidus
    houses = []
    for i, cusp in enumerate(cusps, start=1):
        sign, degree = degree_to_sign(cusp)
        houses.append({
            "number": i,
            "longitude": round(cusp, 4),
            "sign": sign,
            "degree": degree,
        })
    return houses, round(ascmc[0], 4)  # ascmc[0] = Ascendant


def assign_house(planet_longitude: float, house_cusps: list) -> int:
    cusps = [h["longitude"] for h in house_cusps]
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if end < start:
            if planet_longitude >= start or planet_longitude < end:
                return i + 1
        else:
            if start <= planet_longitude < end:
                return i + 1
    return 1


def calculate_aspects(planets: list) -> dict:
    major = []
    minor = []

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1 = planets[i]
            p2 = planets[j]
            diff = abs(p1["longitude"] - p2["longitude"])
            if diff > 180:
                diff = 360 - diff

            for angle, info in MAJOR_ASPECTS.items():
                orb = abs(diff - angle)
                if orb <= info["orb"]:
                    major.append({
                        "planet1": p1["name"],
                        "planet2": p2["name"],
                        "type": info["name"],
                        "angle": angle,
                        "orb": round(orb, 2),
                        "applying": False,
                    })
                    break

            for angle, info in MINOR_ASPECTS.items():
                orb = abs(diff - angle)
                if orb <= info["orb"]:
                    minor.append({
                        "planet1": p1["name"],
                        "planet2": p2["name"],
                        "type": info["name"],
                        "angle": angle,
                        "orb": round(orb, 2),
                    })
                    break

    return {"major": major, "minor": minor}


def calculate_birth_chart(
    birth_date: str,
    birth_time: str,
    birth_lat: float,
    birth_lng: float,
    timezone: str
) -> dict:
    jd = local_to_ut(birth_date, birth_time, timezone)
    planets_raw = calculate_planets(jd)
    houses, ascendant = calculate_houses(jd, birth_lat, birth_lng)

    # Her gezegene ev ata
    planets = []
    for p in planets_raw:
        house = assign_house(p["longitude"], houses)
        planets.append({**p, "house": house})

    aspects = calculate_aspects(planets)

    return {
        "julian_day": jd,
        "ascendant": ascendant,
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "metadata": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "lat": birth_lat,
            "lng": birth_lng,
            "timezone": timezone,
            "house_system": "Placidus",
        }
    }
