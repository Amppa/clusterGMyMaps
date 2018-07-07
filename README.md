# clusterGMyMaps
This is a program to meanshift cluster Google My Maps placemark

Google My Maps is a very useful service to sharing your place point to other.
But when there are too many placemarks in one map, it is wasting time to move from layer to layer.
With this tool, you can cluster placemarks to make it easier to move.

### Environment need
python 3.2+ (due to using iter() in ElementTree)
sklearn and numpy

### Usage
1. Export GoogleMyMaps data to KML (not KMZ)
2. Change KML file name as "input.kml" (There is 2 example)
3. Execute "clusterGoogleMyMapsKml.py"
4. It should generate "output.kml"
5. Import "output.kml" into GoogleMyMaps


### Notice
1. If the input places is too few, the meanshift algorithm may not work. So I set a lower bound to apply clusting (MINIMUM_NUM_OF_POINTS_TO_APPLY_CLUSTER_ALGO = 10)
