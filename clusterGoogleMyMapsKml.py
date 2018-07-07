# -*- coding:utf-8 -*-
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

INPUT_FILE_NAME = "input3.kml"
OUTPUT_FILE_NAME = "output.kml"
MINIMUM_NUM_OF_POINTS_TO_APPLY_CLUSTER_ALGO = 10

namespace = "http://www.opengis.net/kml/2.2"
ET.register_namespace('', namespace)

import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth


def main():

	print("This is a tool to clustering GoogleMyMaps's placemarks by thier coordinate")
	print("This version only regrouping in each layer(folder), so it won't change the layer struction.\n")
	print("Please export GoogleMyMaps file to KML and rename as '" + INPUT_FILE_NAME + "'")
	
	tree = ET.parse(INPUT_FILE_NAME)
	root = tree.getroot()
	
	doc = root.find("{%s}Document" % namespace)
	clusterPlacemarkOfDoc(doc)
	
	tree.write(OUTPUT_FILE_NAME, "UTF-8", xml_declaration=True)
	print("Output done, please import '" + OUTPUT_FILE_NAME + "' into GoogleMyMaps.")

def clusterPlacemarkOfDoc(doc):
	folderGroup = doc.findall("{%s}Folder" % namespace)
	if folderGroup is None:
		clusterPlacemarkInFolder(doc)
	else:
		for folder in folderGroup:
			clusterPlacemarkInFolder(folder)
			print('.', end='')

def clusterPlacemarkInFolder(folder):
	placeDb = []
	parserPlacemarkToDb(folder, placeDb)
	
	
	if len(placeDb) > MINIMUM_NUM_OF_POINTS_TO_APPLY_CLUSTER_ALGO:
		clusterMeanshift(placeDb)
	else:
		sortDb(placeDb)
		print("There are only %d samples in this layer, the cluster algorithm may not work " % len(placeDb), end='')
		print(" so apply sorting algorithm under %d points" % MINIMUM_NUM_OF_POINTS_TO_APPLY_CLUSTER_ALGO)
	
	removePlacemarkElmt(folder)
	appendPlacemarkElmt_fromDbToFolder(placeDb, folder)


def parserPlacemarkToDb(folder, placeDb):
	for placemark in folder.findall("{%s}Placemark" % namespace):
		name = placemark.find('{%s}name' % namespace).text
		
		for coordElmt in placemark.iter('{%s}coordinates' % namespace):
			coord_str = coordElmt.text
			# If it is point type, than it only has one coordinate.
			# Otherwise we only use the last position (e.g. polygon type)
		
		coord_str = coord_str.strip()	# remove space or CRLF
		coord = coord_str.split(',')	# longitude, latitude, alt = coord[0:3]
		coord_long, coord_lat = coord[0:2]
		
		placeDb.append({'name':name, 'x':float(coord_long), 'y':float(coord_lat), 'elmt':placemark})

def clusterMeanshift(placeDb):

	# Because Scikit lib need pure array data as meanshift input,
	# We need to (1)extract Dict to List (2)Run meanshift (3)Use predict to direct back to Dict
	# (1)
	coordList = []
	for node in placeDb:
		coordList.append((node['x'], node['y']))
	
	# (2)
	X = coordList
	bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=500)
	if bandwidth <= 0:
		bandwidth = 100
	ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
	ms.fit(X)
	
	labels = ms.labels_
	cluster_centers = ms.cluster_centers_
	labels_unique = np.unique(labels)
	n_clusters_ = len(labels_unique)
	#print("number of estimated clusters : %d" % n_clusters_)
	#print(cluster_centers)
	
	# (3)
	#print(ms.predict(X))
	for i in range(0, len(placeDb)):
		belong_cluster_id = ms.predict(X)[i]
		(placeDb[i])['cluster_id'] = belong_cluster_id
	
	placeDb.sort(key = lambda s:s['y'])		# Not nessary, I hope there is also sort longitude in cluster
	placeDb.sort(key = lambda s:s['cluster_id'])

def sortDb(placeDict):
	placeDict.sort(key = lambda s:s['x'])
	placeDict.sort(key = lambda s:s['y'])

def removePlacemarkElmt(folder):
	for placemark in folder.findall("{%s}Placemark" % namespace):
		folder.remove(placemark)

def appendPlacemarkElmt_fromDbToFolder(placeDb, folder):
	for node in placeDb:
		folder.append(node['elmt'])

def printAllPlacemarkName(folder):
	for placemark in folder.findall("{%s}Placemark" % namespace):
		name = placemark.find('{%s}name' % namespace).text
		print(name)


if __name__ == "__main__":
	main()