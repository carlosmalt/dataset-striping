import math
import string

# Auxiliary functions to deal with multi-dimensional spaces (regular topologies). They work with any number of dimenstions.

def bboxDiv(bbox, s):
        (coord1, coord2) = bbox
        return (map(lambda x: x/s, coord1), map(lambda x: x/s, coord2))
        
def coordsAdd(coords1, coords2):
        ret = []
        for i in range(len(coords1)):
                ret.append(coords1[i] + coords2[i])
        return ret
                                
def coordsSub(coords1, coords2):
        ret = []
        for i in range(len(coords1)):
                ret.append(coords1[i] - coords2[i])
        return ret
        
def outOfBounds(bbox, coords):
        (coords1, coords2) = bbox
        for i in range(len(coords1)):
                if coords1[i] + coords[i] >= coords2[i]:
                        return True
        return False
        
# Order functions impose a total order on the cells of a a bounding box: the first three (2D, 3D, 4D) are just to show the pattern of row-major as dimensions increase. The fourth one works with any number of dimensions. 
        
def rowMajorOrder2D(bbox, pos):
        d = coordsSub(bbox[1], bbox[0])
        x = pos % d[0]
        y = pos / d[0]
        # print pos, (x, y)
        if outOfBounds(bbox, (x, y)): 
                return None
        return coordsAdd(bbox[0], (x, y))
        
def rowMajorOrder3D(bbox, pos):
        d = coordsSub(bbox[1], bbox[0])
        x = pos % d[0]
        y = (pos % (d[0] * d[1])) / d[0]
        z = pos / (d[0] * d[1])
        if outOfBounds(bbox, (x, y, z)):
                return None
        return coordsAdd(bbox[0], (x, y, z))
        
def rowMajorOrder4D(bbox, pos):
        d = coordsSub(bbox[1], bbox[0])
        x = pos % d[0]
        y = (pos % (d[0] * d[1])) / d[0]
        z = (pos % (d[0] * d[1] * d[2])) / (d[0] * d[1])
        t = pos / (d[0] * d[1] * d[2])
        if outOfBounds(bbox, (x, y, z, t)):
                return None
        return coordsAdd(bbox[0], (x, y, z, t))
        
def rowMajorOrder(bbox, pos):
        d = coordsSub(bbox[1], bbox[0])
        coords = [0] * len(d)
        mod = 1
        div = 1
        for i in range(len(d)):
                if i == len(d) - 1:
                        coords[i] = pos
                else:
                        mod *= d[i]
                        coords[i] = pos % mod
                if i > 0:
                        div *= d[i-1]
                        coords[i] /= div
        if outOfBounds(bbox, coords):
                return None
        return coordsAdd(bbox[0], coords)                        
                

class Iterator:
        '''This Iterator class iterates through a bounding box of cells that are of target size'''
        def __init__(self, objBbox, order, dsName = 'dataset'):
                self.objBbox = objBbox
                self.order = order
                self.dsName = dsName
                self.linPos = 0
                
        def next(self):
                coords = self.order(self.objBbox, self.linPos)
                if coords is None:
                        return None
                self.linPos += 1
                return '%s-%s' % (self.dsName, string.join(map(str, coords), '-'))
                
        def reset(self):
                self.linPos = 0
                

class Partitioning:
        '''The partitioning function becomes more computationally intensive with irregular geometries
        where we need to create indices, or we need to adjust the target size to not create too many
        small objects, or cover cases where cells are significantly larger than the object target
        size. Most importantly, the partitioning function keeps computation out of the critical path.'''
        def __init__(self, iteratorClass, dsName, cellSize, targetObjSize):
                self.iteratorClass = iteratorClass
                self.dsName = dsName
                self.cellSize = cellSize
                self.targetSize = targetObjSize
                
        def getObjBboxConstCube(self, bbox):
                # This translates the bounding box of the dataset into a bounding box of constant-sized cells which define the content of objects.
                # This function assumes that the dataset's cell size is constant
                # It also partitions the dataset into hypercubes with an edge length of "sideLen"
                # These are partitioning choices for a regular topology with constant geometry. Other dataset architectures will have more complex computations and even lookups here.
                sideLen = int(math.pow(self.targetSize / self.cellSize, 1./len(bbox[0])))
                return bboxDiv(bbox, sideLen)
                
        def getObjBboxConst1D(self, bbox):
                # 
                None
                
        def getObjBboxRegGeo(self, bbox):
                # Assumes self.cellSize is a function. Not used yet.
                avgCellSize = (self.cellSize(bbox[0]) + self.cellSize(bbox[1])) / 2
                sideLen = int(math.pow(self.targetSize / avgCellSize, 1./len(bbox[0])))
                return bboxDiv(bbox, sideLen)
                
        def getObjBboxIrregGeo(self, bbox):
                # Assumes self.cellSize(bbox[0]) needs to be looked up. Not implemented yet.
                None

        def getIterator(self, bbox, order):
                return self.iteratorClass(self.getObjBboxConstCube(bbox), order, self.dsName)                
                                
if __name__ == "__main__":
        
        part = Partitioning(Iterator, 'someDatasetName', 8, 8 * 1024**2)
        
        names = part.getIterator(((1024, 1024, 2048, 2048), (3072, 4096, 5120, 6144)), rowMajorOrder)
        
        for i in range(1000):
                name = names.next()
                if name is None:
                        break
                print name
                