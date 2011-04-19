#!/usr/bin/python
from PIL import Image, ImageOps, ImageFilter
import math

images = []
clusters = []
_bord = 2
_blurs = 2
_sizeThreshold = 2
_sizeFactor = 0.5
_threshold = 1.5
_maxDiff = 1000000

class MyImage:
	def __init__(self, img, name):
		self.img = img.copy()
		self.name = name
	def prepare(self):
		src = ImageOps.expand(self.img, border=_bord, fill='white')
		src = Image.eval(src, lambda pix: 255*(pix>179))
		orig = src
		for i in xrange(_blurs):
			src = src.filter(ImageFilter.BLUR)
		src = Image.blend(orig, src, 0.75)
		self.img = src
		

def _RGBToGray(tuple):
	res = 0
	for val in tuple:
		res = 255*res + val
	res = 1.0 * res / (255*255*255)
	return res
	
def distance(x, y):
	X = images[x].img
	Y = images[y].img
	if math.fabs(Y.size[0] - X.size[0]) > _sizeThreshold or math.fabs(Y.size[1] - X.size[1]) > _sizeThreshold:
		return _maxDiff
	size_diff = math.fabs(Y.size[0] * Y.size[1] - X.size[0] * X.size[1])
	if X.size > Y.size:
		X = X.resize(Y.size, Image.ANTIALIAS)
	elif Y.size > X.size:
		Y = Y.resize(X.size, Image.ANTIALIAS)
	seqX = pixelSeq(X)
	seqY = pixelSeq(Y)
	res = 0.
	size = len(seqX)
	for i in xrange(size):
		tmp = seqX[i] - seqY[i]
		res = res + tmp * tmp
	return (math.sqrt(res) + _sizeFactor * size_diff)
	
def inCluster(imgNo, clusterNo):
	for repNo in clusters[clusterNo]:
		if distance(repNo, imgNo) < _threshold:
			return True
	return False

def pixelSeq(img):
	return map(_RGBToGray, img.getdata())
	
def cluster():
	for x in xrange(len(images)):
		added = False
		for c in xrange(len(clusters)):
			if inCluster(x, c):
				added = True
				clusters[c].append(x)
		if not added:
			clusters.append([x])


def blur_image(x):
	src = ImageOps.expand(images[x].img, border=_bord, fill='white')
	src = Image.eval(src, lambda pix: 255*(pix>179))
	orig = src
	for i in xrange(_blurs):
		src = src.filter(ImageFilter.BLUR)
	src = Image.blend(orig, src, 0.75)
	images[x].img = src

if __name__ == '__main__':
    import sys
    if len(sys.argv) not in [2, 3]:
		print 'usage: start.py file_with_list [outputfilename_without_ext]'
		sys.exit(1)
    out_file_name = sys.argv[2] if len(sys.argv) == 3 else 'result'
    file_name = sys.argv[1]
    with open(file_name, 'r') as f:
		for line in f:
			if line[-1] == '\n':
				line = line[0:-1] 
			images.append(MyImage(Image.open(line), line))
		for img in images:
			img.prepare()
		cluster()
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
