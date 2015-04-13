import numpy, random

class KMeans:
    def __init__(self,X,M,K):
        self.X = numpy.array(X,dtype=float)
        self.M = numpy.array(M,dtype=float)
        self.K = K
        
        assert len(self.X.shape) == 2, "Input matrix X is not a two-dimensional array, " \
            "but instead %s-dimensional." % len(self.X.shape)
        assert self.X.shape == self.M.shape, "Input matrix V is not of the same size as " \
            "the indicator matrix M: %s and %s respectively." % (self.X.shape,self.M.shape)
        assert self.K > 0, "K should be greater than 0."
        
        (self.no_points,self.no_coordinates) = self.X.shape
    
    
    """ Initialise the cluster centroids randomly """
    def initialise(self,seed=None):
        if seed:
            random.seed(seed)
        
        self.mins = [column.min() for column in self.X.T]
        self.maxs = [column.max() for column in self.X.T]
        
        self.centroids = [self.random_cluster_centroid() for k in xrange(0,self.K)]
        self.cluster_assignments = numpy.array([-1 for d in xrange(0,self.no_points)])
        self.mask_centroids = numpy.ones(self.K,self.no_coordinates)

    # Randomly place a new cluster centroids, picking uniformly between the min and max of each coordinate
    def random_cluster_centroid(self):
        centroid = []
        for coordinate in xrange(0,self.no_coordinates):
            value = random.uniform(self.mins[coordinate],self.maxs[coordinate])
            centroid.append(value)     
        return centroid    
    
            
    """ Perform the clustering, until there is no change """
    def cluster(self):
        change = True
        while change:
            # First (re)assign data points to the closest cluster centroid, then recompute centroids
            change = self.assignment()
            self.update()


    """ Assign each data point to the closest cluster, and return whether any reassignments were made """
    def assignment(self):
        self.data_point_assignments = [[] for k in xrange(0,self.K)]
        
        change = False
        for d,(data_point,mask) in enumerate(zip(self.X,self.M)):
            old_c = self.cluster_assignments[d]
            new_c = self.closest_cluster(data_point,mask)
            
            self.cluster_assignments[d] = new_c
            self.data_point_assignments[new_c].append(d)
            
            change = (change or old_c != new_c)
        return change
    
    # Compute the MSE to each of the clusters, and return the index of the closest cluster
    def closest_cluster(self,data_point,mask_d):
        closest_index = None
        closest_MSE = None
        for c,(centroid,mask_c) in enumerate(zip(self.centroids,self.mask_centroids)):
            MSE = self.compute_MSE(data_point,centroid,mask_d,mask_c)
            if not closest_MSE or not MSE or MSE < closest_MSE:
                closest_MSE = MSE
                closest_index = c
        return closest_index
    
    # Compute the Euclidean distance between the data point and the cluster centroid.
    # If they have no known values in common, we return None (=infinite distance).
    def compute_MSE(self,x1,x2,mask1,mask2):
        overlap = [i for i,(m1,m2) in enumerate(zip(mask1,mask2)) if (m1 and m2)]
        return None if len(overlap) == 0 else sum([(x1[i]-x2[i])**2 for i in overlap]) / float(len(overlap))
        
        
    """ Update the centroids to the mean of the points assigned to it. 
        If for a coordinate there are no known values, we set this cluster's mask to 0 there. """
    def update(self):
        for c,centroid in enumerate(self.centroids):          
            known_coordinate_values = self.find_known_coordinate_values(c)
            
            # For each coordinate set the centroid to the average, or to None if no values are observed
            for coordinate in xrange(0,self.no_coordinates):
                coordinate_values = known_coordinate_values[coordinate]
                
                if len(known_coordinate_values) == 0:
                    new_coordinate = 0                
                    new_mask = 0
                else:
                    new_coordinate = sum(coordinate_values) / float(len(coordinate_values))
                    new_mask = 1
                
                self.centroids[c][coordinate] = new_coordinate
                self.mask_centroids[c][coordinate] = new_mask
    
    # For a given centroid c, construct a list of lists, each list consisting of
    # all known coordinate values of data points assigned to the centroid.
    def find_known_coordinate_values(self,c):
        assigned_data_indexes = self.data_point_assignments[c]
        data_points = numpy.array([self.X[d] for d in assigned_data_indexes])
        masks = numpy.array([self.M[d] for d in assigned_data_indexes])
        
        lists_known_coordinate_values = [
            [v for d,v in enumerate(data_points.T[coordinate]) if masks[coordinate]]
            for coordinate in xrange(0,self.no_coordinates)
        ]
        return lists_known_coordinate_values