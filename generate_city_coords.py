#!/usr/bin/env python3
"""
Generate city coordinates for SBIR awards data.
Uses the US Cities Database from kelvins/US-Cities-Database.
"""

import json
import csv
import os
import re

# Path to the US cities database
US_CITIES_CSV = "us_cities.csv"

def load_cities_database():
    """Load US cities database from CSV file."""
    cities_db = {}

    with open(US_CITIES_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            city = row['CITY'].upper().strip()
            state = row['STATE_CODE'].upper().strip()
            lat = float(row['LATITUDE'])
            lng = float(row['LONGITUDE'])

            key = f"{city}|{state}"
            # Keep first entry (they're usually the main city)
            if key not in cities_db:
                cities_db[key] = {'lat': lat, 'lng': lng}

    return cities_db

def normalize_city(city):
    """Normalize city name for matching."""
    city = city.upper().strip()
    city = re.sub(r'\s+', ' ', city)
    return city

# State name to abbreviation mapping
state_to_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Puerto Rico': 'PR',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'Guam': 'GU', 'Virgin Islands': 'VI'
}

# City aliases (map alternate names to canonical names in the database)
CITY_ALIASES = {
    # Research/tech parks
    ('RESEARCH TRIANGLE PARK', 'NC'): 'DURHAM',
    ('RTP', 'NC'): 'DURHAM',
    ('RESEARCH TRIANGLE', 'NC'): 'DURHAM',

    # St./Saint variations
    ('ST LOUIS', 'MO'): 'SAINT LOUIS',
    ('ST. LOUIS', 'MO'): 'SAINT LOUIS',
    ('ST PAUL', 'MN'): 'SAINT PAUL',
    ('ST. PAUL', 'MN'): 'SAINT PAUL',
    ('ST PETERSBURG', 'FL'): 'SAINT PETERSBURG',
    ('ST. PETERSBURG', 'FL'): 'SAINT PETERSBURG',

    # Ft./Fort variations
    ('FT WORTH', 'TX'): 'FORT WORTH',
    ('FT. WORTH', 'TX'): 'FORT WORTH',
    ('FT LAUDERDALE', 'FL'): 'FORT LAUDERDALE',
    ('FT. LAUDERDALE', 'FL'): 'FORT LAUDERDALE',
    ('FT COLLINS', 'CO'): 'FORT COLLINS',
    ('FT. COLLINS', 'CO'): 'FORT COLLINS',

    # Mt./Mount variations
    ('MT VIEW', 'CA'): 'MOUNTAIN VIEW',
    ('MT. VIEW', 'CA'): 'MOUNTAIN VIEW',

    # Neighborhoods that map to cities
    ('LA JOLLA', 'CA'): 'SAN DIEGO',
    ('ROSSLYN', 'VA'): 'ARLINGTON',
    ('CRYSTAL CITY', 'VA'): 'ARLINGTON',
    ('PENTAGON', 'VA'): 'ARLINGTON',
    ('TYSONS CORNER', 'VA'): 'MCLEAN',
    ('TYSONS', 'VA'): 'MCLEAN',

    # Direction prefixes
    ('N BILLERICA', 'MA'): 'BILLERICA',
    ('NO BILLERICA', 'MA'): 'BILLERICA',
    ('NORTH BILLERICA', 'MA'): 'BILLERICA',
    ('S SAN FRANCISCO', 'CA'): 'SOUTH SAN FRANCISCO',
    ('SO SAN FRANCISCO', 'CA'): 'SOUTH SAN FRANCISCO',
}

# Manual coordinates for locations not in the database
MANUAL_COORDS = {
    # Research facilities
    ('RESEARCH TRIANGLE PARK', 'NC'): (35.8992, -78.8637),
    ('RTP', 'NC'): (35.8992, -78.8637),

    # Military installations
    ('WRIGHT PATTERSON AFB', 'OH'): (39.8261, -84.0483),
    ('WRIGHT-PATTERSON AFB', 'OH'): (39.8261, -84.0483),
    ('WPAFB', 'OH'): (39.8261, -84.0483),
    ('HANSCOM AFB', 'MA'): (42.4600, -71.2800),
    ('EGLIN AFB', 'FL'): (30.4633, -86.5264),
    ('HILL AFB', 'UT'): (41.1241, -111.9661),
    ('ROBINS AFB', 'GA'): (32.6401, -83.5918),
    ('ANDREWS AFB', 'MD'): (38.8108, -76.8669),
    ('JOINT BASE ANDREWS', 'MD'): (38.8108, -76.8669),
    ('OFFUTT AFB', 'NE'): (41.1183, -95.9127),
    ('LANGLEY AFB', 'VA'): (37.0833, -76.3606),
    ('JOINT BASE LANGLEY-EUSTIS', 'VA'): (37.0833, -76.3606),
    ('NELLIS AFB', 'NV'): (36.2360, -115.0344),
    ('KIRTLAND AFB', 'NM'): (35.0402, -106.6091),
    ('LACKLAND AFB', 'TX'): (29.3847, -98.6169),
    ('JOINT BASE SAN ANTONIO', 'TX'): (29.3847, -98.6169),
    ('JBSA', 'TX'): (29.3847, -98.6169),
    ('FORT BRAGG', 'NC'): (35.1392, -79.0061),
    ('FORT LIBERTY', 'NC'): (35.1392, -79.0061),
    ('FORT MEADE', 'MD'): (39.1086, -76.7434),
    ('FORT BELVOIR', 'VA'): (38.7119, -77.1458),
    ('FORT DETRICK', 'MD'): (39.4369, -77.4380),
    ('ABERDEEN PROVING GROUND', 'MD'): (39.4667, -76.1306),
    ('APG', 'MD'): (39.4667, -76.1306),
    ('PICATINNY ARSENAL', 'NJ'): (40.9486, -74.5378),
    ('REDSTONE ARSENAL', 'AL'): (34.6837, -86.6472),
    ('WHITE SANDS MISSILE RANGE', 'NM'): (32.3891, -106.4784),
    ('WSMR', 'NM'): (32.3891, -106.4784),
    ('STENNIS SPACE CENTER', 'MS'): (30.3648, -89.6003),
    ('CAPE CANAVERAL', 'FL'): (28.3922, -80.6077),
    ('KENNEDY SPACE CENTER', 'FL'): (28.5729, -80.6490),
    ('KSC', 'FL'): (28.5729, -80.6490),
    ('WALLOPS ISLAND', 'VA'): (37.9367, -75.4756),
    ('NASA WALLOPS', 'VA'): (37.9367, -75.4756),
    ('POINT MUGU', 'CA'): (34.1175, -119.1251),
    ('CHINA LAKE', 'CA'): (35.6855, -117.6921),
    ('PATUXENT RIVER', 'MD'): (38.2856, -76.4119),
    ('PAX RIVER', 'MD'): (38.2856, -76.4119),
    ('NAVAL AIR STATION PATUXENT RIVER', 'MD'): (38.2856, -76.4119),
    ('DAHLGREN', 'VA'): (38.3496, -77.0511),
    ('NAVAL SURFACE WARFARE CENTER', 'VA'): (38.3496, -77.0511),
    ('QUANTICO', 'VA'): (38.5220, -77.3184),
    ('MARINE CORPS BASE QUANTICO', 'VA'): (38.5220, -77.3184),
    ('CAMP PENDLETON', 'CA'): (33.3864, -117.5653),
    ('TWENTYNINE PALMS', 'CA'): (34.1355, -116.0545),
    ('CAMP LEJEUNE', 'NC'): (34.6744, -77.4092),
    ('NORFOLK NAVAL BASE', 'VA'): (36.9456, -76.3256),
    ('NAVAL STATION NORFOLK', 'VA'): (36.9456, -76.3256),
    ('PEARL HARBOR', 'HI'): (21.3656, -157.9381),
    ('JOINT BASE PEARL HARBOR-HICKAM', 'HI'): (21.3656, -157.9381),

    # Puerto Rico
    ('SAN JUAN', 'PR'): (18.4655, -66.1057),
    ('AGUADILLA', 'PR'): (18.4275, -67.1541),
    ('MAYAGUEZ', 'PR'): (18.2011, -67.1397),
    ('PONCE', 'PR'): (18.0111, -66.6141),

    # DC area CDPs and unincorporated areas
    ('MCLEAN', 'VA'): (38.9339, -77.1773),
    ('TYSONS', 'VA'): (38.9187, -77.2311),
    ('TYSONS CORNER', 'VA'): (38.9187, -77.2311),
    ('ROSSLYN', 'VA'): (38.8967, -77.0715),
    ('CRYSTAL CITY', 'VA'): (38.8577, -77.0510),
    ('PENTAGON', 'VA'): (38.8720, -77.0559),
    ('GREENBELT', 'MD'): (38.9976, -76.8753),
    ('ADELPHI', 'MD'): (39.0304, -76.9719),
    ('BELTSVILLE', 'MD'): (39.0346, -76.9063),
    ('LEXINGTON PARK', 'MD'): (38.2668, -76.4539),
    ('CALIFORNIA', 'MD'): (38.3001, -76.5064),
    ('INDIAN HEAD', 'MD'): (38.6001, -77.1619),
    ('EDGEWOOD', 'MD'): (39.4187, -76.2944),

    # California CDPs and special areas
    ('EL SEGUNDO', 'CA'): (33.9192, -118.4165),
    ('GOLETA', 'CA'): (34.4358, -119.8276),
    ('LA JOLLA', 'CA'): (32.8328, -117.2713),

    # Northern Virginia CDPs
    ('GREAT FALLS', 'VA'): (39.0054, -77.3014),
    ('ANNANDALE', 'VA'): (38.8304, -77.1966),
    ('BURKE', 'VA'): (38.7934, -77.2714),
    ('CENTREVILLE', 'VA'): (38.8401, -77.4289),
    ('ASHBURN', 'VA'): (39.0437, -77.4875),
    ('STERLING', 'VA'): (39.0062, -77.4286),
    ('DULLES', 'VA'): (38.9531, -77.4565),
    ('SPRINGFIELD', 'VA'): (38.7893, -77.1872),
    ('LORTON', 'VA'): (38.7043, -77.2277),
    ('MERRIFIELD', 'VA'): (38.8740, -77.2261),
    ('WOODBRIDGE', 'VA'): (38.6581, -77.2497),

    # Massachusetts towns
    ('NORTH BILLERICA', 'MA'): (42.5826, -71.2750),
    ('N BILLERICA', 'MA'): (42.5826, -71.2750),

    # Washington DC
    ('WASHINGTON', 'DC'): (38.9072, -77.0369),

    # Ohio suburbs
    ('BEAVERCREEK', 'OH'): (39.7092, -84.0633),
    ('BEAVERCREEK TOWNSHIP', 'OH'): (39.7092, -84.0633),
    ('BEAVERCRK TWP', 'OH'): (39.7092, -84.0633),
    ('BLUE ASH', 'OH'): (39.2320, -84.3785),
    ('LIBERTY TOWNSHIP', 'OH'): (39.3520, -84.3913),
    ('WORTHINGTON', 'OH'): (40.0931, -83.0179),

    # New York suburbs
    ('HALFMOON', 'NY'): (42.8559, -73.7182),
    ('MALTA', 'NY'): (42.9873, -73.7901),
    ('WILLIAMSVILLE', 'NY'): (42.9639, -78.7389),
    ('DIX HILLS', 'NY'): (40.8048, -73.3362),

    # Colorado suburbs
    ('LAKEWOOD', 'CO'): (39.7047, -105.0814),
    ('HIGHLANDS RANCH', 'CO'): (39.5419, -104.9708),

    # Utah suburbs
    ('WEST VALLEY CITY', 'UT'): (40.6916, -112.0011),

    # Maryland suburbs
    ('SPARKS', 'MD'): (39.5429, -76.6527),
    ('CALVERTON', 'MD'): (39.0579, -76.9355),

    # Washington suburbs
    ('TUKWILA', 'WA'): (47.4740, -122.2610),

    # California suburbs
    ('HILLSBOROUGH', 'CA'): (37.5741, -122.3794),
    ('ROLLING HILLS ESTATES', 'CA'): (33.7875, -118.3570),

    # Pennsylvania suburbs
    ('EAST NORRITON', 'PA'): (40.1512, -75.3432),
    ('PENN VALLEY', 'PA'): (40.0476, -75.2485),

    # Georgia suburbs
    ('PEACHTREE CORNERS', 'GA'): (33.9693, -84.2216),

    # New Jersey suburbs
    ('PRINCETON JUNCTION', 'NJ'): (40.3173, -74.6199),
    ('POINT PLEASANT BORO', 'NJ'): (40.0834, -74.0682),

    # Virginia suburbs
    ('BRAMBLETON', 'VA'): (38.9798, -77.5386),

    # Florida suburbs
    ('INLET BEACH', 'FL'): (30.2838, -86.0005),
    ('DAVIE', 'FL'): (26.0629, -80.2517),

    # New Mexico suburbs
    ('LOS RANCHOS', 'NM'): (35.1622, -106.6428),

    # Oklahoma suburbs
    ('MIDWEST CITY', 'OK'): (35.4495, -97.3967),

    # Wisconsin suburbs
    ('MONONA', 'WI'): (43.0628, -89.3340),

    # Missouri suburbs
    ('ELLISVILLE', 'MO'): (38.5925, -90.5873),

    # More suburbs and CDPs
    ('LARGO', 'MD'): (38.8976, -76.8294),
    ('N SALT LAKE', 'UT'): (40.8477, -111.9068),
    ('NORTH SALT LAKE', 'UT'): (40.8477, -111.9068),
    ('NEW MEXICO', 'NM'): (35.0844, -106.6504),  # Default to Albuquerque
    ('FAIRLAWN', 'VA'): (37.2290, -80.1892),
    ('THORNTON', 'CO'): (39.8680, -104.9719),
    ('BERMUDA DUNES', 'CA'): (33.7428, -116.2889),
    ('NORTHFIELD', 'IL'): (42.0981, -87.7809),
    ('SHENANDOAH', 'TX'): (30.1774, -95.4558),
    ('WHITE BEAR LAKE', 'MN'): (45.0836, -93.0097),
    ('MIAMI SHORES', 'FL'): (25.8631, -80.1931),
    ('VESTAVIA', 'AL'): (33.4487, -86.7878),
    ('VESTAVIA HILLS', 'AL'): (33.4487, -86.7878),
    ('MORAINE', 'OH'): (39.7070, -84.2199),
    ('UNIVERSITY PARK', 'IL'): (41.5428, -87.6853),
    ('TREVOSE', 'PA'): (40.1376, -74.9835),
    ('EDGMONT', 'PA'): (39.9362, -75.4799),
    ('TIMONIUM', 'MD'): (39.4370, -76.6194),
    ('CLEVELAND HEIGHTS', 'OH'): (41.5200, -81.5563),
    ('CASTLE VALLEY', 'UT'): (38.6330, -109.4143),
    ('ORO VALLEY', 'AZ'): (32.3909, -110.9665),
    ('WESTON', 'FL'): (26.1003, -80.3998),
    ('BRIER', 'WA'): (47.7843, -122.2751),
    ('RANCHO CASCADES', 'CA'): (34.4258, -118.4570),
    ('CENTENNIAL', 'CO'): (39.5791, -104.8769),
    ('DANIEL ISLAND', 'SC'): (32.8605, -79.9256),
    ('SHERIDAN', 'CO'): (39.6469, -105.0214),
    ('PARKLAND', 'FL'): (26.3100, -80.2334),
    ('ABERDEEN PROVING GROUNDS', 'MD'): (39.4667, -76.1306),
    ('ROSEVILLE', 'MN'): (45.0061, -93.1566),
    ('WOODSIDE', 'CA'): (37.4299, -122.2539),
    ('JONESTOWN', 'TX'): (30.4966, -97.9206),
    ('UNIVERSITY PLACE', 'WA'): (47.2359, -122.5487),
    ('KETTERING', 'OH'): (39.6895, -84.1688),
}

def find_city_coords(city, state_abbrev, cities_db):
    """Find coordinates for a city with fuzzy matching."""
    city = normalize_city(city)

    # Check manual coords first (for military bases, etc.)
    manual_key = (city, state_abbrev)
    if manual_key in MANUAL_COORDS:
        lat, lng = MANUAL_COORDS[manual_key]
        return {'lat': lat, 'lng': lng}

    # Direct lookup in database
    key = f"{city}|{state_abbrev}"
    if key in cities_db:
        return cities_db[key]

    # Check aliases
    if manual_key in CITY_ALIASES:
        aliased = CITY_ALIASES[manual_key]
        key = f"{aliased}|{state_abbrev}"
        if key in cities_db:
            return cities_db[key]

    # Try common variations
    variations = [
        city.replace('SAINT', 'ST'),
        city.replace('ST', 'SAINT'),
        city.replace('ST.', 'SAINT'),
        city.replace('FORT', 'FT'),
        city.replace('FT', 'FORT'),
        city.replace('FT.', 'FORT'),
        city.replace('MOUNT', 'MT'),
        city.replace('MT', 'MOUNT'),
        city.replace('MT.', 'MOUNT'),
        city.replace(' AFB', ''),
        city.replace(' AB', ''),
        city.replace(' AIR FORCE BASE', ''),
        city.replace('-', ' '),
        city.split('-')[0].strip() if '-' in city else None,
        city.split('/')[0].strip() if '/' in city else None,
    ]

    for var in variations:
        if var:
            key = f"{var}|{state_abbrev}"
            if key in cities_db:
                return cities_db[key]

    # Try prefix matching (for compound names like "North Chelmsford")
    city_parts = city.split()
    if len(city_parts) > 1:
        # Remove directional prefix and try
        if city_parts[0] in ('NORTH', 'SOUTH', 'EAST', 'WEST', 'N', 'S', 'E', 'W', 'NO', 'SO'):
            base_city = ' '.join(city_parts[1:])
            key = f"{base_city}|{state_abbrev}"
            if key in cities_db:
                return cities_db[key]

        # Try without last word (for "City" suffix, etc.)
        if city_parts[-1] in ('CITY', 'TOWN', 'TOWNSHIP', 'VILLAGE', 'BOROUGH'):
            base_city = ' '.join(city_parts[:-1])
            key = f"{base_city}|{state_abbrev}"
            if key in cities_db:
                return cities_db[key]

    return None

# Main execution
if __name__ == "__main__":
    # Load awards data
    with open('awards_data.json') as f:
        data = json.load(f)

    # Aggregate cities by state with award counts
    city_awards = {}
    for award in data['awards']:
        state = award.get('state', '')
        city = award.get('city', '').strip().upper()
        if state and city:
            key = (city, state)
            if key not in city_awards:
                city_awards[key] = {'awards': 0, 'funding': 0}
            city_awards[key]['awards'] += 1
            city_awards[key]['funding'] += award.get('amount', 0)

    print(f"Found {len(city_awards)} unique city/state combinations in awards data")

    # Load cities database
    cities_db = load_cities_database()
    print(f"Loaded {len(cities_db)} cities from database")

    # Build the final coordinates data
    print("\nMatching cities...")
    city_coords = {}
    unmatched = []

    for (city, state), stats in city_awards.items():
        if state not in state_to_abbrev:
            continue

        abbrev = state_to_abbrev[state]
        coords = find_city_coords(city, abbrev, cities_db)

        if coords:
            if abbrev not in city_coords:
                city_coords[abbrev] = []
            city_coords[abbrev].append({
                'city': city.title(),
                'lat': coords['lat'],
                'lng': coords['lng'],
                'awards': stats['awards'],
                'funding': round(stats['funding'] / 1000000, 2)
            })
        else:
            unmatched.append((city, state, stats['awards']))

    # Count how many cities we matched
    total_matched = sum(len(cities) for cities in city_coords.values())
    total_awards_matched = sum(c['awards'] for cities in city_coords.values() for c in cities)
    total_awards = sum(s['awards'] for s in city_awards.values())

    print(f"\nMatched {total_matched}/{len(city_awards)} cities ({100*total_matched/len(city_awards):.1f}%)")
    print(f"Awards coverage: {total_awards_matched}/{total_awards} ({100*total_awards_matched/total_awards:.1f}%)")

    # Sort unmatched by award count
    unmatched.sort(key=lambda x: -x[2])

    if unmatched:
        print(f"\nTop 30 unmatched cities (by awards):")
        for city, state, awards in unmatched[:30]:
            abbrev = state_to_abbrev.get(state, '??')
            print(f"  {city}, {abbrev}: {awards} awards")

        print(f"\nTotal unmatched awards: {sum(x[2] for x in unmatched)}")

    # Sort cities by awards within each state
    for abbrev in city_coords:
        city_coords[abbrev].sort(key=lambda x: -x['awards'])

    # Save to file
    with open('city_coords.json', 'w') as f:
        json.dump(city_coords, f, indent=2)

    print(f"\nSaved city coordinates to city_coords.json")
    print(f"States covered: {len(city_coords)}")
