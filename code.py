from typing import Any, Iterable
import csv
import json
import config
import pygeos
import logging

def open_csv(filename: str) -> tuple[list[str], list[list[Any]]]:
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        name_columns = next(reader)
        rows = []
        for row in reader:
            rows.append(row[:])
    return name_columns, rows

def open_json(filename: str) -> dict[str, Any]:
    with open(filename) as f:
        data = json.load(f)
    return data['features']

def compute_centroids(points: Iterable[tuple[float, float]], territories: dict[str, Any])-> Iterable[tuple[str, float, float]]:
    centroids = {}
    for iris in territories:
        tree = pygeos.STRtree(points)
        if len(iris['geometry']['coordinates']) == 1:
            if len(iris['geometry']['coordinates'][0]) > 1:
                polygon_final = pygeos.polygons([iris['geometry']['coordinates'][0][0]], holes=[iris['geometry']['coordinates'][0][1]])[0]
            else:
                polygon_final = pygeos.polygons(iris['geometry']['coordinates'][0])[0]
        else:
            liste_polygon = []
            for i in range(len(iris['geometry']['coordinates'])):
                if len(iris['geometry']['coordinates'][i]) > 1:
                    polygon = pygeos.polygons([iris['geometry']['coordinates'][i][0]], holes=[iris['geometry']['coordinates'][i][1]])[0]
                else:
                    polygon = pygeos.polygons(iris['geometry']['coordinates'][i])[0]
                    liste_polygon.append(polygon)
            polygon_final = pygeos.multipolygons(liste_polygon)
        points_in_IRIS = tree.query(polygon_final, predicate='contains')
        if len(points_in_IRIS) != 0: 
            n = len(points_in_IRIS)
            coord = pygeos.get_coordinates(points[points_in_IRIS[:]])
            centroid_iris = (sum(coord)/n).tolist()
            tree_check = pygeos.STRtree([pygeos.points(centroid_iris)])
            ind = tree_check.query(polygon_final, predicate='contains')
            if ind.size == 0:
                centroid_iris = 'Centroid not in IRIS !'
            centroids[iris['properties']['NOM_IRIS']] = centroid_iris
        else:
            centroids[iris['properties']['NOM_IRIS']] = 'No points in IRIS'
            # Later, we could compute centroid_iris as the geographic center of the IRIS
    return centroids

def convert_csv_array_to_points(columns: list[str], rows:list[list[Any]]):
    mes_points = []
    index_x = columns.index('x')
    index_y = columns.index('y')
    for row_num, row in enumerate(rows):
        point = []
        point.append(float(row[index_x]))
        point.append(float(row[index_y]))
        mes_points.append(point)
    return pygeos.points(mes_points)#.tolist()

if __name__ == '__main__':
    name_columns, rows = open_csv('adresses-france.csv')
    points = convert_csv_array_to_points(name_columns, rows)
    liste_IRIS = open_json(config.IRIS_FILENAME)
    centroids = compute_centroids(points, liste_IRIS)
    logging.info(f'Here is the dictionnary of density based center of mass: {centroids}')