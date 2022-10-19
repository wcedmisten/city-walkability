import json


def get_cities():
    abbreviation_map = {}

    with open("abbreviations.json") as f:
        abbreviations = json.load(f)
        for abbrev in abbreviations:
            abbreviation_map[abbrev["name"]] = abbrev["abbreviation"]

    with open("populous_cities.json") as f:
        pop_cities = json.load(f)

        city_list = []

        for city in pop_cities[:100]:
            state = abbreviation_map[city["state"]].lower()
            city = city["city"].strip().lower().replace(" ", "-")
            city_list.append((city, state))

        return city_list