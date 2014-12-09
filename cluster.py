from math import sqrt
import sys




def hcluster(clusters, m=0):
	print len(clusters)
	if m == 2:
		return clusters
	cdist = {}
	clusters2 = clusters
	for c in clusters:
		clusters2 = clusters2[1:]
		for c2 in clusters2:
			cdist.setdefault(cdistance(c, c2),{}).append((c,c2))
	mcdist = min(cdist)
	print mcdist
	cluster = set(list(group_by(flatten(cdist[mcdist]))))
	print cluster
	print clusters
	#return hcluster(clusters,m+1)

def read_voxels(fname="voxels1.csv", header=False):
	points = []
	f = file(fname,'r')
	lines = f.xreadlines()
	if header:
		print 'Skipped', lines.next()
	for l in lines:
		z, y, x, = [int(x.strip()) for x in l.split(',')]
		points.append((x, y, z,))
	return points

def voxels_to_pixels(voxels):
	pixels = set([])
	for (x,y,_) in voxels:
		pixels.add((x,y))
	return list(pixels)

def euclidean_distance(p, p2): return sqrt(sum(map(lambda x,x2: (x-x2)**2, p, p2)))

def get_neighbours(points, p, clust, dist):
	neighbours = []
	i = len(points)
	while (i > 0):
		np = points[i-1]
		if euclidean_distance(p, np) <= dist:
			points.remove(np)
			i = len(points)
			clust.append(np)
			neighbours.append(np)
		i-=1
	return neighbours

def bfcluster(points, dist=sqrt(2)):
	clusters = []
	while (len(points)):
		p = points.pop()
		cluster = [p]
		pointstovisit = get_neighbours(points, p, cluster, dist)
		while (len(pointstovisit)):
			n = pointstovisit.pop()
			pointstovisit += get_neighbours(points, n, cluster, dist)
		clusters.append(cluster)
		print len(points), len(cluster), len(clusters)
	return clusters

def write_clusters(fname="", clusters=None):
	f = file(fname, 'w')
	for (clusnum, cluster) in enumerate(clusters):
		for p in cluster:
			#print clusnum,voxel per line
			f.write("%s,%s\n" % (str(clusnum), ','.join(map(str,p))))
	f.flush()
	f.close()

def read_clusters(fname=""):
	f = file(fname, 'r')
	clusters = dict()
	for l in f.xreadlines():
		clusnum_p = [int(x) for x in l.split(',')]
		clusnum = clusnum_p[0]
		p = clusnum_p[1:]
		clusters.setdefault(clusnum, []).append(p)
	return clusters


if __name__ == '__main__2':

	args = sys.argv[1:]
	if not args:
		print 'Usage'
		print '<name of file>'
		exit()

	for fname in args:
		print 'Doing', fname
		voxels = read_voxels(fname, header=True)
		print "Number of voxels"
		print len(voxels)
		clusters = bfcluster(voxels, dist=sqrt(2))
		write_clusters("clusters_%s" % fname, clusters)
		clusters = read_clusters("clusters_%s" % fname)
		print "Number of clusters", len(clusters)
		total = 0
		for c in clusters:
			total+=len(clusters[c])
		print "Number of voxels"
		print total

#--------------------------------------------------
# def clusters_2D(clusters):
# 	voxels = dict()
# 	minx = miny = minz = maxx= maxy = maxz = 0
# 	for c in clusters:
# 		for vox in clusters[c]:
# 			voxels.update({vox:c})
# 			x,y,z, = vox
# 			if x <= minx:
# 				minx = x
# 			if x > maxx:
# 				maxx = x
# 			if y <= miny:
# 				miny = y
# 			if y > maxy:
# 				maxy = y
# 			if z <= minz:
# 				minz = z
# 			if z > maxz:
# 				maxz = z
# 	all_overlapping_clusters = set([])
# 	for x in range(minx,maxx):
# 		for y in range(miny,maxy):
# 			overlapping_clusters = tuple(set([voxels[(x,y,z)] for z in range(minz,maxz) if (x,y,z) in voxels]))
# 			if len(overlapping_clusters) > 1:
# 				print x,y, overlapping_clusters
# 				all_overlapping_clusters.add(overlapping_clusters)
# 	all_neighbouring_clusters  = set([])
# 	for x in range(minx,maxx):
# 		for y in range(miny,maxy):
# 		 	r = [-1,0,+1]
# 			neighbouring_points = [(x+a,y+b) for a in r for b in r]
# 			neighbouring_clusters = tuple(set([voxels[(x,y,z)] for z in range(minz,maxz) for (x,y) in neighbouring_points if (x,y,z) in voxels]))
# 			if len(neighbouring_clusters) > 1:
# 				print x,y, neighbouring_clusters
# 				all_neighbouring_clusters.add(neighbouring_clusters)
# 
# 	return all_overlapping_clusters, all_neighbouring_clusters
#-------------------------------------------------- 



#--------------------------------------------------
# def get_clusters_to_merge(clusters):
# 	cdist = {}
# 	clusters_to_merge = [set([c]) for c in sorted(clusters)]
# 	for i in sorted(clusters):
# 		mclusters = set()
# 		for j in sorted(clusters):
# 			if i >= j:
# 				continue
# 			c = clusters[i]
# 			c2 = clusters[j]
# 			d=cdistance(c,c2)
# 			#print d
# 			#mark clusters to merge
# 			if d <= sqrt(2):
# 				mclusters.add(i)
# 				mclusters.add(j)
# 				if set([i]) in clusters_to_merge:
# 					clusters_to_merge.remove(set([i]))
# 				if set([j]) in clusters_to_merge:
# 					clusters_to_merge.remove(set([j]))
# 		#merge clusters
# 		if mclusters:
# 			clusters_to_merge.append(mclusters) 
# 	return clusters_to_merge
#-------------------------------------------------- 

#--------------------------------------------------
# def write_clusters_to_merge(fname="", list_of_clusters=None):
# 	f = file(fname, 'w')
# 	for clusters in list_of_clusters:
# 		f.write("%s\n" % ','.join(map(str, clusters)))
# 	f.flush()
# 	f.close()
#-------------------------------------------------- 

#--------------------------------------------------
# def read_clusters_to_merge(fname=""):
# 	f = file(fname, 'r')
# 	list_of_clusters = []
# 	for l in f.xreadlines():
# 		list_of_clusters.append(set([int(x) for x in l.split(',')]))
# 	return list_of_clusters
#-------------------------------------------------- 


#--------------------------------------------------
# def merge_clusters(mclusters):
# 	n = len(mclusters)
# 	for i in range(n):
# 		cm = mclusters.pop(0)
# 		ccm = [c for c in mclusters if cm.intersection(c)]
# 		#remove them from clusters to merge list
# 		for c in ccm:
# 			mclusters.remove(c)
# 		cm = reduce(lambda x, y: x.union(y), ccm, cm)
# 		mclusters.append(cm)
# 	return mclusters
#-------------------------------------------------- 


#--------------------------------------------------
# if __name__ == '__main__':
# 
# 	args = sys.argv[1:]
# 	if not args:
# 		print 'Usage'
# 		print '<name of file>'
# 		exit()
# 
# 	for fname in args:
# 		print 'Doing', fname
# 		clusters = bfcluster(fname)
# 		write_clusters("clusters_%s" % fname, clusters)
# 		clusters = read_clusters("clusters_%s" % fname)
# 		print "Number of clusters", len(clusters)
# 		total = 0
# 		for c in clusters:
# 			total+=len(clusters[c])
# 		print 'Number of points', total
#-------------------------------------------------- 

	## no need to merge clusters anymore
		#--------------------------------------------------
		# mclusters = get_clusters_to_merge(clusters)
		# write_clusters_to_merge("clusters_to_merge_%s" % fname, mclusters)
		# mclusters = read_clusters_to_merge("clusters_to_merge_%s" % fname)
		# print 'Number of merges', len(mclusters)
		#-------------------------------------------------- 

		#--------------------------------------------------
		# mclusters = merge_clusters(mclusters)
		#-------------------------------------------------- 

		#--------------------------------------------------
		# merged_clusters = []
		# for mc in mclusters:
		# 	newclust = []
		# 	for c in mc:
		# 		newclust+=clusters[c]
		# 	merged_clusters.append(newclust)
		#-------------------------------------------------- 

		#--------------------------------------------------
		# write_clusters("merged_clusters_%s" % fname, merged_clusters)
		# clusters = read_clusters("merged_clusters_%s" % fname)
		# print 'Number of clusters', len(merged_clusters)
		# total = 0
		# for c in clusters:
		# 	total+=len(clusters[c])
		# print 'Number of points', total
		#-------------------------------------------------- 


#--------------------------------------------------
# def flatten(x):
# 	"""flatten(sequence) -> list
# 
# 	Returns a single, flat list which contains all elements retrieved
# 	from the sequence and all recursively contained sub-sequences
# 	(iterables).
# 
# 	Examples:
# 	>>> [1, 2, [3,4], (5,6)]
# 	[1, 2, [3, 4], (5, 6)]
# 	>>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
# 	[1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""
# 
# 	result = []
# 	for el in x:
# 		#if isinstance(el, (list, tuple)):
# 		if hasattr(el, "__iter__") and not isinstance(el, basestring):
# 			result.extend(flatten(el))
# 		else:
# 			result.append(el)
# 	return result
#-------------------------------------------------- 

#--------------------------------------------------
# def group_by(l, n=3):
# 	if len(l) % n != 0:
# 		print 'warning', l, 'not divisible in groups of', n
# 	for i in range(0,len(l),n):
# 		yield tuple(l[i:i+n])
#-------------------------------------------------- 


def read_clusters(fname="clusters_1_100.csv", header=False):
	clusters = {}
	f = file(fname,'r')
	lines = f.xreadlines()
	if header:
		print 'Skipped', lines.next()
	for l in lines:
		c, z, y, x, = [int(x.strip()) for x in l.split(',')]
		clusters.setdefault(c,[]).append((x, y, z,))
	return clusters

def cdistance(cluster, cluster2):
	dist = {}
	for p in cluster:
		for p2 in cluster2:
			dist[euclidean_distance(p, p2)] = (p, p2)
	return min(dist)

def inter_cluster_distances(fname):
	clusters = read_clusters(fname)
	clusters2 = clusters.keys()
	for c in clusters:
		clusters2 = clusters2[1:]
		for c2 in clusters2:
			print ','.join(map(str,((c, c2, "%.3f" % cdistance(clusters[c], clusters[c2])))))

if __name__ == '__main__':
	args = sys.argv[1:]
	fname = args[0]
	inter_cluster_distances(fname)


