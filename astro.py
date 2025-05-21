import swisseph as swe
from datetime import datetime
import pytz

# Define constants
AYANAMSA = 24.0  # Lahiri Ayanamsa for sidereal zodiac conversion
zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Function to normalize degrees (0 to 360 range)
def normalize_degrees(deg):
    return deg % 360

# Function to convert tropical positions to sidereal
def tropical_to_sidereal(tropical_deg):
    sidereal_deg = tropical_deg - AYANAMSA
    return normalize_degrees(sidereal_deg)

# Function to calculate the Ascendant
def calculate_ascendant(jd_ut, latitude, longitude):
    flags = swe.FLG_SIDEREAL
    ayanamsa = swe.get_ayanamsa(jd_ut)  # Get Ayanamsa for sidereal conversion
    ascendant_info = swe.houses_ex(jd_ut, latitude, longitude, b'A', flags)
    ascendant_deg = ascendant_info[0][0]  # Ascendant degree
    asc_index = int(ascendant_deg // 30)
    ascendant_sign = zodiac_signs[asc_index]
    return ascendant_sign, normalize_degrees(ascendant_deg - ayanamsa)

# Function to calculate planetary positions using pyswisseph
def calculate_planet_positions(date_of_birth, time_of_birth, latitude, longitude):
    # Time zone conversion to UTC
    time_of_birth_utc = pytz.timezone('Asia/Kolkata').localize(datetime.strptime(f"{date_of_birth} {time_of_birth}", "%Y-%m-%d %H:%M"))
    time_of_birth_utc = time_of_birth_utc.astimezone(pytz.utc)

    # Convert the time to Julian Day
    jd_ut = swe.julday(time_of_birth_utc.year, time_of_birth_utc.month, time_of_birth_utc.day, 
                       time_of_birth_utc.hour + time_of_birth_utc.minute / 60)

    # Calculate Ascendant
    ascendant_sign, ascendant_degrees = calculate_ascendant(jd_ut, latitude, longitude)
    print(f"Ascendant: {ascendant_sign} ({ascendant_degrees:.2f}°)")

    # Get planetary positions
    planets_positions = {}
    planets = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Rahu (North Node)': swe.MEAN_NODE,  # Rahu (North Node)
        'Ketu (South Node)': swe.MEAN_NODE   # Ketu is always 180° from Rahu
    }

    for planet_name, planet_id in planets.items():
        # Get the planetary positions
        planet_info = swe.calc_ut(jd_ut, planet_id, flags=swe.FLG_SIDEREAL)
        planet_sidereal_deg = planet_info[0][0]  # Get longitude
        planet_house = int(((planet_sidereal_deg - ascendant_degrees) % 360) // 30) + 1

        # Add to results
        planets_positions[planet_name] = (planet_sidereal_deg, planet_house)

    return planets_positions

# Example usage
date_of_birth = '1996-03-20'
time_of_birth = '10:20'
latitude = 29.4739  # Muzaffarnagar latitude
longitude = 77.7041  # Muzaffarnagar longitude

positions = calculate_planet_positions(date_of_birth, time_of_birth, latitude, longitude)
for planet, (degrees, house) in positions.items():
    print(f"{planet}: {degrees%30:.2f}° (House {house})")
