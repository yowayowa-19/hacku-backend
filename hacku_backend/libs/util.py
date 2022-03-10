from geopy.distance import geodesic

def distance(first: tuple[float], second: tuple[float]) -> float:
    return geodesic(first, second).km


def calc_distance(latlong_list: list[tuple[float]]) -> float:
    result = 0
    [
        result := result + distance(f, s)
        for f, s in zip(latlong_list[:-1], latlong_list[1:])
    ]
    return result