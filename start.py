#!/usr/bin/python
from PIL import Image, ImageOps, ImageFilter
from numpy import linalg, array
import math
import random

images = []
clusters = []
_bord = 2
_blurs = 2
_sizeThreshold = 2
_sizeFactor = 0.
_threshold = 1.45
_maxDiff = 1000000
_joins = 2
_cutoff = 15

def getNewSize(oldSize):
	newHeight = 15
	if (oldSize[1] > 15):
		newHeight = 25
	elif (oldSize[1] < 5):
		newHeight = 5
	newWidth = 15
	if (oldSize[0] > 15):
		newWidth = 25
	elif (oldSize[0] < 5):
		newWidth = 5
	return (newWidth, newHeight)

def _RGBToGray(tuple):
	res = 0
	for val in tuple:
		res = 255*res + val
	res = 1.0 * res / (255*255*255)
	return res
	

class MyImage:
	def __init__(self, img, name):
		self.img = img.copy()
		self.name = name
		self.distances = {name: 0.}
		self.sizePenalty = {name: 0.}
	
	def prepare(self):
		self.origSize = self.img.size
		src = self.img.resize(getNewSize(self.origSize), Image.BICUBIC)
		src = ImageOps.expand(src, border=_bord, fill='white')
		src = Image.eval(src, lambda pix: 255*(pix>179))
		orig = src
		for i in xrange(_blurs):
			src = src.filter(ImageFilter.BLUR)
		src = Image.blend(orig, src, 0.75)
		self.img = src
		self.arr = array(map(_RGBToGray, self.img.getdata()))
	
	def distance(self, other):	
		if other.name in self.distances:
			return self.distances[other.name] + _sizeFactor * self.sizePenalty[other.name]
		if (math.fabs(other.origSize[0] - self.origSize[0]) > _sizeThreshold or math.fabs(other.origSize[1] - self.origSize[1]) > _sizeThreshold) or (self.arr.size != other.arr.size):
			result = _maxDiff
			size_diff = 0.
		else:
			size_diff = math.fabs(other.origSize[0] * other.origSize[1] - self.origSize[0] * self.origSize[1])
		 	result = linalg.norm(self.arr - other.arr)
		self.distances[other.name] = result
		other.distances[self.name] = result
		self.sizePenalty[other.name] = size_diff
		other.sizePenalty[self.name] = size_diff
		return result + _sizeFactor * size_diff
	

	
def inCluster(imgNo, clusterNo):
	clusterSize = len(clusters[clusterNo])
	if (clusterSize) > 15:
		repNoSeq = random.sample(clusters[clusterNo], 15)
	else:
		repNoSeq = clusters[clusterNo]
	for repNo in repNoSeq:
		if images[repNo].distance(images[imgNo]) < _threshold:
			return True
	return False

def join(c, d):
	cSize = len(clusters[c])
	dSize = len(clusters[d])
	sampleSize = _cutoff
	if (cSize <= _cutoff) or (dSize <= _cutoff):
		sampleSize = min(cSize, dSize)
	cReps = random.sample(clusters[c], sampleSize)
	dReps = random.sample(clusters[d], sampleSize)
	similar = 0
	found = 0
	for cRep in clusters[c]:
		for dRep in clusters[d]:
			if images[cRep].distance(images[dRep]) < _threshold:
				return True
	return False

def sizeCompare(a, b):
	return cmp(len(b), len(a))

def sortBySize():
	clusters.sort(sizeCompare)

def cluster():
	for x in xrange(len(images)):
		added = False
		for c in xrange(len(clusters)):
			if inCluster(x, c):
				added = True
				clusters[c].append(x)
		if not added:
			clusters.append([x])

def joinClusters():
	global _threshold
	global _sizeFactor
	global _addedThreshold
	_threshold += 0.125
	_sizeFactor += 0.2
	for x in xrange(len(clusters)):
		toJoin = []
		for y in xrange(x+1, len(clusters)):
			if join(x, y):
				toJoin.append(y)
		for y in reversed(toJoin):
			clusters[x].extend(clusters.pop(y))

if __name__ == '__main__':
    import sys
    if len(sys.argv) not in [2, 3]:
		print 'usage: start.py file_with_list [outputfilename_without_ext]'
		sys.exit(1)
    out_file_name = sys.argv[2] if len(sys.argv) == 3 else 'result'
    file_name = sys.argv[1]
    with open(file_name, 'r') as f:
		random.seed()
		for line in f:
			if line[-1] == '\n':
				line = line[0:-1] 
			images.append(MyImage(Image.open(line), line))
		for img in images:
			img.prepare()
		cluster()
		print 'clusters: %0s' %  len(clusters)
		for i in xrange(_joins):
			sortBySize()
			joinClusters()
			print 'clusters: %0s' %  len(clusters)
		sortBySize()
		with open(out_file_name + '.txt', 'w') as out:
			for cluster in clusters:
				for i in cluster:
					out.write(images[i].name + ' ')
				out.write('\n')
		with open(out_file_name + '.html', 'w') as out:
			out.write('<html><head><title>clustering</title></head><body>')
			for cluster in clusters:
				for i in cluster:
					out.write('<img src="' + images[i].name + '"/>')
				out.write('<hr/>')
			out.write('</body></html>')
