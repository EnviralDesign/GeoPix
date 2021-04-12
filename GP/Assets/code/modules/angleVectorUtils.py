import numpy as np
import math

def vectDif_2_eulerRot(vector_orig, vector_fin):
	"""Calculate the rotation matrix required to rotate from one vector to another.

	For the rotation of one vector to another, there are an infinit series of rotation matrices
	possible.  Due to axially symmetry, the rotation axis can be any vector lying in the symmetry
	plane between the two vectors.	Hence the axis-angle convention will be used to construct the
	matrix with the rotation axis defined as the cross product of the two vectors.	The rotation
	angle is the arccosine of the dot product of the two unit vectors.

	Given a unit vector parallel to the rotation axis, w = [x, y, z] and the rotation angle a,
	the rotation matrix R is::

			  |	 1 + (1-cos(a))*(x*x-1)	  -z*sin(a)+(1-cos(a))*x*y	 y*sin(a)+(1-cos(a))*x*z |
		R  =  |	 z*sin(a)+(1-cos(a))*x*y   1 + (1-cos(a))*(y*y-1)	-x*sin(a)+(1-cos(a))*y*z |
			  | -y*sin(a)+(1-cos(a))*x*z   x*sin(a)+(1-cos(a))*y*z	 1 + (1-cos(a))*(z*z-1)	 |


	@param R:			The 3x3 rotation matrix to update.
	@type R:			3x3 numpy array
	@param vector_orig: The unrotated vector defined in the reference frame.
	@type vector_orig:	numpy array, len 3
	@param vector_fin:	The rotated vector defined in the reference frame.
	@type vector_fin:	numpy array, len 3
	"""
	
	R = np.matrix([[1., 0, 0], [0, 1., 0], [0, 0, 1.]])
	
	# Convert the vectors to unit vectors.
	vector_orig = vector_orig / np.linalg.norm(vector_orig)
	vector_fin = vector_fin / np.linalg.norm(vector_fin)

	# The rotation axis (normalised).
	axis = np.cross(vector_orig, vector_fin)
	axis_len = np.linalg.norm(axis)
	if axis_len != 0.0:
		axis = axis / axis_len

	# Alias the axis coordinates.
	x = axis[0]
	y = axis[1]
	z = axis[2]

	# The rotation angle.
	angle = math.acos(np.dot(vector_orig, vector_fin))

	# Trig functions (only need to do this maths once!).
	ca = math.cos(angle)
	sa = math.sin(angle)
	# print(ca, sa)
	# Calculate the rotation matrix elements.
	R[0,0] = 1.0 + (1.0 - ca)*(x**2 - 1.0)
	R[0,1] = -z*sa + (1.0 - ca)*x*y
	R[0,2] = y*sa + (1.0 - ca)*x*z
	R[1,0] = z*sa+(1.0 - ca)*x*y
	R[1,1] = 1.0 + (1.0 - ca)*(y**2 - 1.0)
	R[1,2] = -x*sa+(1.0 - ca)*y*z
	R[2,0] = -y*sa+(1.0 - ca)*x*z
	R[2,1] = x*sa+(1.0 - ca)*y*z
	R[2,2] = 1.0 + (1.0 - ca)*(z**2 - 1.0)
	
	sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
	
	singular = sy < 1e-6
 
	if	not singular :
		x = math.atan2(R[2,1] , R[2,2])
		y = math.atan2(-R[2,0], sy)
		z = math.atan2(R[1,0], R[0,0])
	else :
		x = math.atan2(-R[1,2], R[1,1])
		y = math.atan2(-R[2,0], sy)
		z = 0
 
	return np.rad2deg( np.array([x, y, z]) )