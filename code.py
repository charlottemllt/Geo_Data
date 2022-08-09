from typing import Any, Iterable
import csv
import json
import config
import pygeos
import time

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
    return data

def compute_centroids(points: Iterable[tuple[float, float]], territories: dict[str, Any])-> Iterable[tuple[str, float, float]]:
    centroids = {}
    for iris in territories:
        tree = pygeos.STRtree(points)

        if len(iris['geometry']['coordinates']) == 1:
            if len(iris['geometry']['coordinates'][0]) > 1:
                polygon = pygeos.polygons([iris['geometry']['coordinates'][0][0]], holes=[iris['geometry']['coordinates'][0][1]])[0]
            else:
                polygon = pygeos.polygons(iris['geometry']['coordinates'][0])[0]
        else:
            liste_polygon = []
            for i in range(len(iris['geometry']['coordinates'])):
                if len(iris['geometry']['coordinates'][i]) > 1:
                    polygon = pygeos.polygons([iris['geometry']['coordinates'][i][0]], holes=[iris['geometry']['coordinates'][i][1]])[0]
                else:
                    polygon = pygeos.polygons(iris['geometry']['coordinates'][i])[0]
                    liste_polygon.append(polygon)
            polygon = pygeos.multipolygons(liste_polygon)
        
        points_in_IRIS = tree.query(polygon, predicate='contains')
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
    return pygeos.points(mes_points)#.tolist()

if __name__ == '__main__':
    timer0 = time.time()
    name_columns, rows = open_csv('df_test2.csv')
    timer1 = time.time()
    points = convert_array_to_points(name_columns, rows)
    timer2 = time.time()
    liste_IRIS = open_json(config.IRIS_FILENAME)
    timer3 = time.time()
    centroids = compute_centroids(points, liste_IRIS['features'])
    timer4 = time.time()
    print(centroids)

    print('elapsed time for open_csv', timer1 - timer0, 's')
    print('elapsed time for convert_array_to_points', timer2 - timer1, 's')
    print('elapsed time for open_json', timer3 - timer2, 's')
    print('elapsed time for compute_centroids', timer4 - timer3, 's')