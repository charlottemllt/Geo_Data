from typing import Any, Iterable
import csv
import json
import config
import pygeos
import numpy as np

def open_csv(filename: str) -> tuple[list[str], list[list[Any]]]:
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        name_columns = next(reader)
        rows = []
        for row in reader:
            rows.append(row[:])
    return name_columns, rows

def open_json(filename: str):
    with open(filename) as f:
        data = json.load(f)
    #for feature in data['features']:
        #print(feature['properties']['NOM_IRIS'])
        #print(feature['properties']['INSEE_COM'])
        #print(feature['geometry']['coordinates'][0][0])
        #break
    return data

def compute_centroids(points: Iterable[tuple[float, float]], territories: dict[str, Any])-> Iterable[tuple[str, float, float]]:
    centroids = {}
    for iris in territories:
        if iris['properties']['INSEE_COM'] in ["01002", "97605"]:
            tree = pygeos.STRtree(points)
            points_in_IRIS = tree.query(pygeos.polygons(iris['geometry']['coordinates'])[0][0], predicate='contains')
            if len(points_in_IRIS) != 0:
                n = len(points_in_IRIS)
                coord = pygeos.get_coordinates(points[points_in_IRIS[:]])
            centroid_iris = sum(coord)/n
            centroid_iris = centroid_iris.tolist()

            tree_check = pygeos.STRtree([pygeos.points(centroid_iris)])
            ind = tree_check.query(pygeos.polygons(iris['geometry']['coordinates'])[0][0], predicate='contains')
            if ind.size == 0:
                centroid_iris = 'Centroid not in IRIS !'
            centroids[iris['properties']['NOM_IRIS']] = centroid_iris
    return centroids

def convert_array_to_points(columns, rows):
    mes_points = []
    index_x = columns.index('x')
    index_y = columns.index('y')
    for row_num, row in enumerate(rows):
        point = []
        point.append(float(row[index_x]))
        point.append(float(row[index_y]))
        mes_points.append(point)
    print(mes_points)
    return pygeos.points(mes_points)#.tolist()

def empty(): 
    my_list = [[2, 4], [2, 6], [2, 8]]
    my_set_point = {e for l in my_list for e in l}

    thisdict = {
    "brand": "Ford",
    "model": "Mustang",
    "year": 1964
    }
    pass

if __name__ == '__main__':
    array = open_csv('df_test2.csv')
    name_columns, rows = array
    points = convert_array_to_points(name_columns, rows)

    liste_IRIS = open_json(config.IRIS_FILENAME)
    centroids = compute_centroids(points, liste_IRIS['features'])
    print(centroids)