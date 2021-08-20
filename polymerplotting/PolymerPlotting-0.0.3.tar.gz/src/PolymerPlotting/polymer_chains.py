import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

################################################################################

def genRotMat(axis,angle):
    """Returns a general rotation matrix;
     when given a normalised axis vector (u)
     and the right handed rotation angle (theta),
      as given in Materials part II C6"""
    m = np.cos(angle)
    n = np.sin(angle)
    u = axis

    rot_mat_pt1 = np.array([[m, u[2]*n, -u[1]*n], [-u[2]*n, m, u[0]*n], [u[1]*n, -u[0]*n, m]])
    rotmat = np.outer(u,u)*(1-m) + rot_mat_pt1

    return rotmat

################################################################################

def plot_chains(chain_list):
    """ Takes a list of 'Polymer_Chain' objects and plots them together on a single canvas"""

    fig = plt.figure()
    ax = plt.axes(projection="3d")

    max_coords = np.zeros(3)
    min_coords = np.zeros(3)

    for chain in chain_list:
        if chain:
            points = chain.coords

            max_coords = np.maximum(np.max(points, axis=0), max_coords)
            min_coords = np.minimum(np.min(points, axis=0), min_coords)

            ax.plot3D(points[:,0],points[:,1],points[:,2], label=chain.name)


    centre = (max_coords + min_coords)/2
    axis_range = np.amax(max_coords - min_coords)*0.55

    ax.set_xlim(centre[0]-axis_range, centre[0]+axis_range)
    ax.set_ylim(centre[1]-axis_range, centre[1]+axis_range)
    ax.set_zlim(centre[2]-axis_range, centre[2]+axis_range)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    fig.legend()
    fig.tight_layout()
    return fig

################################################################################

class Polymer_Chain():
    # initialise counter of all chains
    count = 0

    def __init__(self, chain_length):
        self.name = None
        self._length = chain_length
        self._coords = None
        self.CoM = None
        self.end2end = None
        self.theor_end2end = self.theoretical_end2end()
        self.RoG = None
        self.theor_RoG = self.theoretical_RoG()
        Polymer_Chain.count += 1

    # length defined as a property num. of segments num. # of points !!!
    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, chain_length):
        self._length = chain_length

    # coords defined as a property
    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, chain_coords):
        self._coords = chain_coords

    # name getter and setter methods
    def get_name(self):
        return self.name

    def set_name(self, chain_name):
        self.name = chain_name

    # describe method
    def describe(self):
        print(self.name)

    # centre of mass calculator
    def calculate_CoM(self):
        if type(self._coords) != "NoneType":
            self.CoM = np.sum(self._coords, axis = 0) / (self.length + 1)
        else:
            print("Need to generate coords with '.calculate_coords()' before trying to find CoM")
        return self.CoM

    # radius of gyration calculator
    def calculate_RoG(self):
        self.calculate_CoM()
        self.RoG = np.sqrt(np.sum((self._coords - self.CoM * np.ones(np.shape(self._coords)))**2) / (self.length + 1))
        return self.RoG

    # end to end distance calculator
    def calculate_end2end(self):
        if type(self._coords) != "NoneType":
            self.end2end = np.sqrt(np.sum((self._coords[0,:] - self._coords[-1,:])**2))
            return self.end2end
        else:
            print("Need to generate coords with '.calculate_coords()' before trying to find end to end distance")

    # theoretical end to end distance calulator: <r> = a * N^0.5
    def theoretical_end2end(self):
        self.theor_end2end = np.sqrt(self.length)
        return self.theor_end2end

    # theoretical radius of gyration calculator: <rg> = <r> / 6^0.5
    def theoretical_RoG(self):
        self.theor_RoG = self.theor_end2end / np.sqrt(6)
        return self.theor_RoG

################################################################################

class Random_Walk_Chain(Polymer_Chain):
    # set segment offset as class variable
    segment_offset = 1

    # initialise count of instances of this class
    count = 0

    # initialise the object, getting the bits from the superclass and incrementing the class instance counter
    def __init__(self, chain_length):
        super().__init__(chain_length)
        Random_Walk_Chain.count += 1
        self.set_name("RW Chain {}".format(Random_Walk_Chain.count))

    def calculate_coords(self):

        number_of_points = self._length + self.segment_offset

        # determine the orientation of each link
        theta = np.random.rand(number_of_points) * np.pi
        phi = np.random.rand(number_of_points) * 2 * np.pi

        # from angles determine each link as a vector
        adVects = np.zeros((number_of_points,3))
        adVects[:,0] = np.sin(theta)*np.cos(phi)
        adVects[:,1] = np.sin(theta)*np.sin(phi)
        adVects[:,2] = np.cos(theta)*np.ones((number_of_points))

        # sum cumulatively over the additional vectors to get each point in the chain
        self._coords = adVects.cumsum(axis = 0)

################################################################################

class Freely_Rotating_Chain(Polymer_Chain):
    # set segment offest as class variable
    segment_offset = 1

    # initialise count of instances of this class
    count = 0

    # initialise the object, getting the bits from the superclass and incrementing the class instance counter
    def __init__(self, chain_length, chain_bond_angle=109.5):
        super().__init__(chain_length)
        self.bond_angle = chain_bond_angle    # chain bond angle preset to carbon value
        Freely_Rotating_Chain.count += 1
        self.set_name("FR Chain {}".format(Freely_Rotating_Chain.count))

    def calculate_coords(self):

        number_of_points = self._length + self.segment_offset

        # set number of points and initialise coordinates, make first link along z axis
        points = np.zeros((number_of_points,3))
        start = np.array([0,0,1])
        points[1,:] += start

        # define the bend angle from the bond angle (fixed for freely rot), and the random torsion angles
        theta = (180 - self.bond_angle) * (np.pi/180)
        phi = np.random.rand(number_of_points) * 2 * np.pi

        # from angles determine additional vectors, one to be added after each rotation
        adVects = np.zeros((number_of_points,3))
        adVects[:,0] = np.sin(theta)*np.cos(phi)
        adVects[:,1] = np.sin(theta)*np.sin(phi)
        adVects[:,2] = np.cos(theta)*np.ones((number_of_points))

        # add the additional vector to the previous one (which lies along the z axis) and then rotate the new vector to the z axis
        row = 0
        for i in range(number_of_points - 2):
            row = i+2

            # determine new chunk to be added and add it
            adVect = adVects[row, :]
            newRow = points[row-1,:] + adVect
            points[row,:] += newRow

            # find rotation axis unit vector (normalised by the rotation angle, which should always be the bond angle)
            u = np.cross(start,adVect) / np.sin(theta)

            # form rotation matrix
            rotmat = genRotMat(u,theta)

            # apply rotation matrix
            points = np.transpose(np.matmul(rotmat,np.transpose(points)))

        self._coords = points

################################################################################

class Rotational_Isomeric_Chain(Polymer_Chain):
    # set segment offest as class variable
    segment_offset = 1

    # initialise count of instances of this class
    count = 0

    # initialise the object, getting the bits from the superclass and incrementing the class instance counter
    def __init__(self, chain_length, chain_bond_angle = 109.5, chain_torsion_positions = 3, chain_trans_bias = 2):
        super().__init__(chain_length)
        self.bond_angle = chain_bond_angle                  # chain bond angle preset to carbon value
        self.torsion_positions = chain_torsion_positions    # chain torsion positions set to 3 as is standard for carbon
        self.trans_bias = chain_trans_bias                  # chain trans bias set to 2, as from part II C10 p16 P(trans) ~= 2*P(gauche) ~= 2*P(gauche-)
        Rotational_Isomeric_Chain.count += 1
        self.set_name("RI Chain {}".format(Rotational_Isomeric_Chain.count))

    def calculate_coords(self):

        number_of_points = self._length + self.segment_offset

        # set number of points and initialise coordinates, make first link along z axis
        points = np.zeros((number_of_points,3))
        z_axis = np.array([0,0,1])
        y_axis = np.array([0,1,0])
        points[1,:] += z_axis


        # define the bend angle, and the randomly selected torsion angles
        phi_options = (np.arange(self.torsion_positions) * 2 * np.pi /self.torsion_positions) + np.pi
        phi_weights = np.ones(self.torsion_positions)
        phi_weights[0] *= self.trans_bias
        phi_weights = phi_weights/np.sum(phi_weights)
        phi = np.random.choice(phi_options, size=number_of_points, p=phi_weights)

        theta = (180 - self.bond_angle) * (np.pi/180)

        # from angles determine additional vectors, one to be added after each rotation
        adVects = np.zeros((number_of_points,3))
        adVects[:,0] = np.sin(theta)*np.cos(phi)
        adVects[:,1] = np.sin(theta)*np.sin(phi)
        adVects[:,2] = np.cos(theta)*np.ones((number_of_points))

        # add the additional vector to the previous one (which lies along the z axis) and then rotate the new vector to the z axis
        row = 0
        for i in range(number_of_points - 2):
            row = i+2

            # determine new chunk to be added and add it
            adVect = adVects[row, :]
            newRow = points[row-1,:] + adVect
            points[row,:] += newRow

            # define matrices so that new segment aligns with z axis and previous one lies in xz plane (these could be vectorised so that they don't have to be done in the for loop, as are't dependent on previous rows)
            rotmatZ = genRotMat(z_axis,phi[row])
            rotmatY = genRotMat(y_axis,theta)

            # apply rotation matrices
            points = np.transpose(np.matmul(rotmatY,np.matmul(rotmatZ,np.transpose(points))))

        self._coords = points

################################################################################
