"""
Golf Courses Database

Simple dictionary of popular golf courses with their locations.
For MVP - expand to database later.
"""

from typing import Optional, Dict


# Popular golf courses with their locations and altitudes
COURSES: Dict[str, Dict] = {
    "tpc scottsdale": {
        "city": "Scottsdale",
        "state": "AZ",
        "country": "US",
        "altitude_ft": 1500,
    },
    "pebble beach": {
        "city": "Pebble Beach",
        "state": "CA",
        "country": "US",
        "altitude_ft": 50,
    },
    "st andrews": {
        "city": "St Andrews",
        "state": "Scotland",
        "country": "UK",
        "altitude_ft": 30,
    },
    "bandon dunes": {
        "city": "Bandon",
        "state": "OR",
        "country": "US",
        "altitude_ft": 100,
    },
    "castle pines": {
        "city": "Castle Rock",
        "state": "CO",
        "country": "US",
        "altitude_ft": 6500,
    },
    "pinehurst no 2": {
        "city": "Pinehurst",
        "state": "NC",
        "country": "US",
        "altitude_ft": 525,
    },
    "pinehurst": {
        "city": "Pinehurst",
        "state": "NC",
        "country": "US",
        "altitude_ft": 525,
    },
    "torrey pines": {
        "city": "La Jolla",
        "state": "CA",
        "country": "US",
        "altitude_ft": 340,
    },
    "bethpage black": {
        "city": "Farmingdale",
        "state": "NY",
        "country": "US",
        "altitude_ft": 90,
    },
    "augusta national": {
        "city": "Augusta",
        "state": "GA",
        "country": "US",
        "altitude_ft": 450,
    },
    "whistling straits": {
        "city": "Sheboygan",
        "state": "WI",
        "country": "US",
        "altitude_ft": 620,
    },
    "kiawah island": {
        "city": "Kiawah Island",
        "state": "SC",
        "country": "US",
        "altitude_ft": 10,
    },
    "chambers bay": {
        "city": "University Place",
        "state": "WA",
        "country": "US",
        "altitude_ft": 200,
    },
    "shinnecock hills": {
        "city": "Southampton",
        "state": "NY",
        "country": "US",
        "altitude_ft": 60,
    },
    "oakmont": {
        "city": "Oakmont",
        "state": "PA",
        "country": "US",
        "altitude_ft": 1000,
    },
    "winged foot": {
        "city": "Mamaroneck",
        "state": "NY",
        "country": "US",
        "altitude_ft": 200,
    },
    "merion": {
        "city": "Ardmore",
        "state": "PA",
        "country": "US",
        "altitude_ft": 400,
    },
    "olympic club": {
        "city": "San Francisco",
        "state": "CA",
        "country": "US",
        "altitude_ft": 500,
    },
    "sawgrass": {
        "city": "Ponte Vedra Beach",
        "state": "FL",
        "country": "US",
        "altitude_ft": 15,
    },
    "tpc sawgrass": {
        "city": "Ponte Vedra Beach",
        "state": "FL",
        "country": "US",
        "altitude_ft": 15,
    },
    "riviera": {
        "city": "Pacific Palisades",
        "state": "CA",
        "country": "US",
        "altitude_ft": 200,
    },
    "congressional": {
        "city": "Bethesda",
        "state": "MD",
        "country": "US",
        "altitude_ft": 350,
    },
    "east lake": {
        "city": "Atlanta",
        "state": "GA",
        "country": "US",
        "altitude_ft": 1050,
    },
    "bay hill": {
        "city": "Orlando",
        "state": "FL",
        "country": "US",
        "altitude_ft": 100,
    },
    "muirfield village": {
        "city": "Dublin",
        "state": "OH",
        "country": "US",
        "altitude_ft": 900,
    },
    "quail hollow": {
        "city": "Charlotte",
        "state": "NC",
        "country": "US",
        "altitude_ft": 750,
    },
    "colonial": {
        "city": "Fort Worth",
        "state": "TX",
        "country": "US",
        "altitude_ft": 650,
    },
    "harbour town": {
        "city": "Hilton Head Island",
        "state": "SC",
        "country": "US",
        "altitude_ft": 10,
    },
    "shadow creek": {
        "city": "Las Vegas",
        "state": "NV",
        "country": "US",
        "altitude_ft": 2000,
    },
    "wolf creek": {
        "city": "Mesquite",
        "state": "NV",
        "country": "US",
        "altitude_ft": 3500,
    },
}


def get_course_location(course_name: str) -> Optional[Dict]:
    """
    Look up course location by name.

    Args:
        course_name: Name of the golf course

    Returns:
        Dictionary with city, state, country, altitude_ft or None if not found
    """
    key = course_name.lower().strip()
    return COURSES.get(key)


def search_courses(query: str) -> list:
    """
    Search for courses matching a query.

    Args:
        query: Search query (partial match)

    Returns:
        List of matching course names
    """
    query_lower = query.lower().strip()
    return [name for name in COURSES.keys() if query_lower in name]


def get_all_courses() -> list:
    """
    Get list of all available courses.

    Returns:
        List of course names
    """
    return list(COURSES.keys())
