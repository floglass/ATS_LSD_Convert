import pandas as pd
import os
import glob
import geopandas


def make_examples(path_list):
    output_csv = pd.DataFrame(columns=['LSD', 'Latitude', 'Longitude'])
    for path in path_list:
        temp = pd.read_csv(path, header=0)
        temp = temp[['LSD', 'Latitude', 'Longitude']]
        output_csv = output_csv.append(temp, ignore_index=True)
    return output_csv


def load_shapefile(shp_path=None):
    """Read a shapefile and load it into a geopandas GeoDataFrame.
    WARNING: the default file is huge (5.7M lines) and will take ~10min to load"""
    gdf = geopandas.read_file(shp_path)
    print(gdf.loc[0:10])
    return gdf


def format_gdf(geodataframe, drop=True):
    """WARNING: On ATS dataset this is very slow! ATS has 5.7 million lines..."""
    if drop is True:
        geodataframe = geodataframe.drop(columns=['FILE_NAME', 'TRM', 'M', 'RGE', 'TWP', 'SEC', 'QS', 'LS',
                                                  'DESCRIPTOR'])

    # recompute Latitude and Longitude (!slow)
    centroids = geodataframe.centroid
    geodataframe['Latitude'] = centroids.y
    geodataframe['Longitude'] = centroids.x
    return geodataframe


def save_to_csv(geodataframe):
    path = 'D:\ATS-LSD\ATS_Polygons_SHP_Geographic\ATS_V4-1_LSD_wLatLon.csv'
    geodataframe.to_csv(path, columns=['PID', 'Latitude', 'Longitude'], index=False)
    path_shp = 'D:\ATS-LSD\ATS_Polygons_SHP_Geographic\ATS_V4-1_LSD_wLatLon.shp'
    geodataframe.to_file(path_shp)
    print('..Files saved')
    return


if __name__ == '__main__':
    os.chdir('D:\ATS-LSD\LSD_examples')
    csv_list = glob.glob('[!_]*csv')  # exclude any file starting with '_'
    compiled_csv = make_examples(csv_list)
    compiled_csv.to_csv('_total_examples.csv', index=False)
