#! /usr/bin/env python

#############################################################################
#
# (C) 2021 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This sample script is not supported by Cadence Design Systems, Inc.
# It is provided freely for demonstration purposes only.
# SEE THE WARRANTY DISCLAIMER AT THE BOTTOM OF THIS FILE.
#
#############################################################################

import numpy as np
import math


"""
Utility classes that mimic the behavior of the Glyph pwu::* utilites.
"""

class GlyphUtility:
    tolerance = 1e-7

class Vector2(object):
    """ Utility functions for two dimensional vectors, which are represented
        as a list of two real values.
    """

    def __init__(self, *args):
        """ Construct a 2D vector, all zeroes by default.  """
        self.vector_ = None
        if len(args) == 0:
            self.vector_ = np.zeros([2])
        elif len(args) == 1:
            if isinstance(args[0], (list, tuple)) and len(args[0]) == 2:
                self.vector_ = np.array([float(i) for i in args[0]])
            elif isinstance(args[0], np.ndarray):
                self.vector_ = args[0]
            elif isinstance(args[0], Vector2):
                self.vector_ = args[0].vector_
        elif len(args) == 2:
            self.vector_ = np.array([float(i) for i in args])

        if self.vector_ is None:
            raise ValueError("Invalid parameter %s" % str(args))
        elif self.vector_.size != 2 or self.vector_.ndim != 1:
            raise ValueError("Vector2 must be a list/tuple of 2 values")

    def __eq__(self, other):
        """ Check for equality of two vectors """
        return self.equal(other)

    def __add__(self, other):
        """ Add two vectors together and return the result as a new Vector2 """
        return Vector2(np.add(tuple(self), tuple(other)))
    
    def __sub__(self, other):
        """ Subtract one vector from another and return the result as a
            new Vector2.
        """
        return Vector2(np.subtract(tuple(self), tuple(other)))
    
    def __mul__(self, other):
        """ Multiply the components of a vector by either the components of
            another vector or a scalar and return the result as a new
            Vector2.
        """
        if isinstance(other, (float, int)):
            other = (other, other)

        return Vector2(np.multiply(tuple(self), tuple(other)))
        
    def __truediv__(self, other):
        """ Divide the components of a vector by either the components of
            another vector or a scalar and return the result as a new
            Vector2.
        """
        if isinstance(other, (float,int)):
            other = (other, other)

        return Vector2(np.true_divide(tuple(self), tuple(other)))

    def __div__(self, other):
        """ Divide the components of a vector by either the components of
            another vector or a scalar and return the result as a new
            Vector2.
        """
        return self.__truediv__(other)

    def __str__(self):
        """ Return a string representation of a Vector2 """
        return str(tuple(self))

    def __iter__(self):
        return (e for e in self.vector_)
 
    def __len__(self):
        return len(self.vector_)

    def index(self, i):
        """ Return a component of a Vector2 """
        return self.vector_[i]
    
    @property
    def x(self):
        """ The X component of a Vector2 """
        return self.vector_[0]

    @x.setter
    def x(self, v):
        """ Set the X component of a Vector2 """
        self.vector_[0] = v
    
    @property
    def y(self):
        """ The X component of a Vector2 """
        return self.vector_[1]

    @y.setter
    def y(self, v):
        """ Set the Y component of a Vector2 """
        self.vector_[1] = v
    
    def equal(self, other, tolerance=GlyphUtility.tolerance):
        """ Check for equality between two vectors within an optional tolerance
        """
        return np.linalg.norm(np.subtract(tuple(self), tuple(other))) \
                <= tolerance
        
    def notEqual(self, other, tolerance=GlyphUtility.tolerance):
        """ Check for inequality between two vectors within an optional
            tolerance
        """
        return not self.equal(other, tolerance)
        
    def add(self, vec2):
        """ Add the components of two vectors and return the result as a new
            Vector2
        """
        return self + vec2
    
    def subtract(self, vec2):
        """ Subtract one vector from another and return the result as a new
            Vector2
        """
        return self - vec2
    
    def negate(self):
        """ Negate the component values and return the result as a new Vector2
        """
        return self * -1
    
    def scale(self, scalar):
        """ Scale the component values by a scalar and return the result as
            a new Vector2
        """
        return self * scalar
    
    def divide(self, scalar):
        """ Divide the component values by a scalar and return the result as
            a new Vector2
        """
        return self / scalar
    
    def multiply(self, vec2):
        """ Multiply the component values of a vector by the component values
            of another vector and return the result as a new Vector2
        """
        return self * vec2
    
    def dot(self, vec2):
        """ Return the scalar dot product of two vectors """
        return np.dot(self.vector_, vec2.vector_)
    
    def normalize(self):
        """ Return the normalized form of a vector as a new Vector2 """
        norm = np.linalg.norm(self.vector_)
        if norm == 0:
            raise ValueError('Vector is zero vector')
        else:
            return self / norm
        
    def length(self):
        """ Return the scalar length of a vector """
        return np.linalg.norm(self.vector_)

    @staticmethod
    def zero():
        """ Return the 2-dimensional zero vector """
        return Vector2(0.0, 0.0)
    
    @staticmethod
    def minimum(vec1, vec2):
        """ Return the minimum components of two vectors as a new Vector2 """
        return Vector2(np.minimum(tuple(vec1), tuple(vec2)))
    
    @staticmethod
    def maximum(vec1, vec2):
        """ Return the maximum components of two vectors as a new Vector2 """
        return Vector2(np.maximum(tuple(vec1), tuple(vec2)))


class Vector3(object):
    """ Utility functions for three dimensional vectors, which are represented
        as a list of three real values.
    """
    def __init__(self, *args):
        """ Construct a 3D vector, all zeroes by default. """
        self.vector_ = None
        if len(args) == 0:
            self.vector_ = np.zeros([3])
        elif len(args) == 1:
            if isinstance(args[0], (list, tuple)) and len(args[0]) == 3:
                self.vector_ = np.array([float(i) for i in args[0]])
            elif isinstance(args[0], np.ndarray):
                self.vector_ = args[0]
            elif isinstance(args[0], Vector3):
                self.vector_ = args[0].vector_
            elif isinstance(args[0], Vector2):
                self.vector_ = args[0].vector_
                self.vector_.append(0.0)
        elif len(args) == 3:
            self.vector_ = np.array([float(i) for i in args])

        if self.vector_ is None:
            raise ValueError("Invalid parameter %s" % str(args))
        elif self.vector_.size != 3 or self.vector_.ndim != 1:
            raise ValueError("Vector3 must be 3 float values")

    def __eq__(self, other):
        """ Check for equality of two vectors """
        return self.equal(other)

    def __add__(self, other):
        """ Add two vectors together and return the result as a new Vector3.
        """
        return Vector3(np.add(tuple(self), tuple(other)))
    
    def __sub__(self, other):
        """ Subtract one vector from another and return the result as a
            new Vector3.
        """
        return Vector3(np.subtract(tuple(self), tuple(other)))
    
    def __mul__(self, other):
        """ Multiply the components of a vector by either the components of
            another vector or a scalar and return the result as a new
            Vector3.
        """
        if isinstance(other, (float, int)):
            other = (other, other, other)

        return Vector3(np.multiply(self.vector_, tuple(other)))

    def __truediv__(self, other):
        """ Divide the components of a vector by either the components of
            another vector or a scalar and return the result as a new
            Vector3.
        """
        if isinstance(other, (float, int)) and other != 0.0:
            return Vector3(1.0 / other * self.vector_)
        else:
            return np.true_divide(self.vector_, tuple(other))
    
    def __div__(self, other):
        """ Divide the components of a vector by either the components of
            another vector or a scalar and return the result as a new
            Vector3.
        """
        return self.__truediv__(other)
    
    def __str__(self):
        """ Return a string representation of a Vector3 """
        return str(tuple(self))

    def __iter__(self):
        return (e for e in self.vector_)

    def __len__(self):
        return len(self.vector_)

    def index(self, i):
        """ Return a component of a Vector3 """
        return self.vector_[i]
    
    @property
    def x(self):
        """ The X component of a Vector3 """
        return self.vector_[0]

    @x.setter
    def x(self, v):
        """ Set the X component of a Vector3 """
        self.vector_[0] = v
    
    @property
    def y(self):
        """ The Y component of a Vector3 """
        return self.vector_[1]

    @y.setter
    def y(self, v):
        """ Set the Y component of a Vector3 """
        self.vector_[1] = v
    
    @property
    def z(self):
        """ The Z component of a Vector3 """
        return self.vector_[2]
    
    @z.setter
    def z(self, v):
        """ Set the Z component of a Vector3 """
        self.vector_[2] = v
    
    def equal(self, other, tolerance=GlyphUtility.tolerance):
        """ Check for equality between two vectors within an optional tolerance
        """
        return np.linalg.norm(np.subtract(tuple(self), tuple(other))) \
                <= tolerance
    
    def notEqual(self, other, tolerance=GlyphUtility.tolerance):
        """ Check for inequality between two vectors within an optional
            tolerance
        """
        return not self.equal(other, tolerance)
        
    def add(self, other):
        """ Add the components of two vectors and return the result as a new
            Vector3
        """
        return self + other
    
    def subtract(self, other):
        """ Subtract one vector from another and return the result as a new
            Vector3
        """
        return self - other
    
    def negate(self):
        """ Negate the component values and return the result as a new Vector3
        """
        return self * -1.0
    
    def scale(self, scalar):
        """ Scale the component values by a scalar and return the result as
            a new Vector3
        """
        return self * scalar
    
    def divide(self, scalar):
        """ Divide the component values by a scalar and return the result as
            a new Vector3
        """
        return self / scalar
    
    def multiply(self, scalar):
        """ Multiply the component values of a vector by the component values
            of another vector and return the result as a new Vector3
        """
        return self * scalar
    
    def cross(self, other):
        """ Return the cross product of two vectors as a new Vector3 """
        return Vector3(np.cross(self.vector_, tuple(other)))
    
    def dot(self, other):
        """ Return the scalar dot product of two vectors """
        return np.dot(self.vector_, tuple(other))
    
    def normalize(self):
        """ Return the normalized form of a vector as a new Vector3 """
        norm = np.linalg.norm(self.vector_)
        if norm == 0:
            raise ValueError('Vector is zero vector')
        else:
            return self / norm
    
    def length(self):
        """ Return the scalar length of a vector """
        return np.linalg.norm(self.vector_)
    
    def distanceToLine(self, pt, direction):
        """ Return the scalar distance from a vector to a line defined
            by a point and direction.
        """
        lineVec = Vector3(direction).normalize()
        ptVec = self - Vector3(pt)
        ptProj = lineVec * ptVec.dot(lineVec)
        return (ptVec - ptProj).length()
    
    @staticmethod
    def zero():
        """ Return the 3-dimensional zero vector """
        return Vector3(0.0, 0.0, 0.0)
    
    @staticmethod
    def minimum(vec1, vec2):
        """ Return the minimum components of two vectors as a new Vector3 """
        return Vector3(np.minimum(tuple(vec1), tuple(vec2)))
    
    @staticmethod
    def maximum(vec1, vec2):
        """ Return the maximum components of two vectors as a new Vector3 """
        return Vector3(np.maximum(tuple(vec1), tuple(vec2)))
    
    @staticmethod
    def affine(scalar, vec1, vec2):
        """ Return a new Vector3 that is the affine combination of two vectors
        """
        return Vector3(np.add(
            np.multiply(tuple(vec1), (scalar, scalar, scalar)),
            np.multiply(tuple(vec2), (1.0-scalar, 1.0-scalar, 1.0-scalar))))
    
    @staticmethod
    def barycentric(pt, vec1, vec2, vec3, clamp=False):
        """ Return a new Vector3 that has the barycentric coordinates of
            the given point in the frame of the given three vectors.
        """
        pt = Vector3(pt)
        v1 = Vector3(vec1)
        v2 = Vector3(vec2)
        v3 = Vector3(vec3)
        a = b = 0.0

        v12 = v2 - v1
        v13 = v3 - v1

        cross = v12.cross(v13)
        area = 0.5 * cross.length()

        if area == 0.0:
            mode = 23
            len12 = v12.length()
            len13 = v13.length()
            len23 = (v2 - v3).length()
            if len12 >= len13:
                if len12 >= len23:
                    mode = 11 if len12 == 0.0 else 12
            elif len13 >= len23:
                mode = 13

            if mode == 12:
                a = (pt - v2).length() / len12
                b = 1.0 - a
            elif mode == 13:
                a = (pt - v3).length() / len13
                b = 0.0
            elif mode == 23:
                a = 0.0
                b = (pt - v3).legnth() / len23
            else:  # mode = 11
                a = 1.0
                b = 0.0
        else:
            cross1 = (v2 - pt).cross(v3 - pt)
            a = 0.5 * cross1.length() / area
            if cross.dot(cross1) < 0.0:
                a = -a
            cross2 = (pt - v1).cross(v13)
            b = 0.5 * cross2.length() / area
            if cross.dot(cross2) < 0.0:
                b = -b

        a = 0.0 if clamp and a < 0.0 else a
        b = 0.0 if clamp and b < 0.0 else b
        b = 1.0 - a if clamp and (a + b) > 1.0 else b

        return Vector3((a, b, 1.0 - a - b))


class Quaternion(object):
    """ Utility functions for quaternions, which are represented as a list
        of four real values (x, y, z, and angle)
    """

    def __init__(self, axis=(0.0, 0.0, 0.0), angle=0, _quat=None):
        """ Construct a quaternion, with a degenerate axis and zero angle
            by default
        """
        if _quat is not None:
            self.quat_ = _quat
            # normalize
            self.quat_ /= np.sqrt(sum(k*k for k in self.quat_))
            self.angle_ = np.degrees(np.arccos(self.quat_[0]) * 2)
            self.axis_ = Vector3(self.quat_[1:4])
            self.axis_ = self.axis_ / np.sin(np.radians(self.angle_ / 2))
        elif len(axis) == 3:
            if not isinstance(axis, Vector3):
                axis = Vector3(axis)
            if axis.length() == 0.0 or angle == 0.0:
                self.quat_ = (1.0, 0.0, 0.0, 0.0)
                self.angle_ = 0.0
                self.axis_ = axis
            else:
                length = axis.length()

                # clamp the angle between -2*pi and +2*pi
                while angle < -360.0:
                    angle += 360.0
                while angle > 360.0:
                    angle -= 360.0

                if angle == 90.0 or angle == -270.0:
                    w = math.sqrt(0.5)
                    u = w / length
                elif angle == 180.0 or angle == -180.0:
                    w = 0.0
                    u = 1.0 / length
                elif angle == -90.0 or angle == 270.0:
                    w = math.sqrt(0.5)
                    u = -w / length
                else:
                    angle = angle / 2.0
                    w = np.cos(np.radians(angle))
                    u = np.sin(np.radians(angle)) / length

                # normalize, since that's what Glyph does
                self.quat_ = (w, u*axis.x, u*axis.y, u*axis.z)
                self.quat_ /= np.sqrt(sum(k*k for k in self.quat_))

                angleRadians = np.arccos(w) * 2.0
                self.angle_ = np.degrees(angleRadians)
                self.axis_ = Vector3(self.quat_[1:4]) / np.sin(angleRadians/2.0)
        else:
            raise ValueError("Invalid parameter")

        if len(self.quat_) != 4:
            raise ValueError("Quaternion must be list/tuple of 4 values")
        
    def __mul__(self, other):
        """ Return the quaternion product of two quaternions as a new Quaternion
        """
        if isinstance(other, (float, int)):
            return Quaternion(_quat=(self.quat_ * other))
        else:
            w0, x0, y0, z0 = self.quat_
            w1, x1, y1, z1 = other.quat_
            quatProduct = np.array(
                    [w1*w0 - x1*x0 - y1*y0 - z1*z0, \
                     w1*x0 + x1*w0 + y1*z0 - z1*y0, \
                     w1*y0 + y1*w0 + z1*x0 - x1*z0, \
                     w1*z0 + z1*w0 + x1*y0 - y1*x0])
            return Quaternion(_quat=quatProduct)
    
    def __truediv__(self, other):
        """ Return the quaternion divided by a scalar as a new Quaternion """
        other = (other, other, other, other)
        return Quaternion(_quat=(np.true_divide(self.quat_, other)))

    def __div__(self, other):
        return self.__truediv__(other)

    def __str__(self):
        """ Return the string form of a Quaternion as axis and angle """
        return "(%s, %f)" % (str(tuple(self.axis_)), self.angle_)

    def __iter__(self):
        return (e for e in (tuple(self.axis_) + (self.angle_,)))
    
    @property
    def axis(self):
        """ Return the rotation axis of a quaternion as a Vector3 """
        return self.axis_
    
    @property
    def angle(self):
        """ Return the scalar rotation angle in degrees """
        return self.angle_
    
    def equal(self, quat2):
        """ Compare two quaternions for equality """
        return np.array_equal(self.quat_, quat2.quat_)
    
    def notEquals(self, quat2):
        """ Compare two quaternions for inequality """
        return not self.equal(quat2)
    
    def rotate(self, quat2):
        """ Rotate a quaternion by another quaternion and return the result
            as a new Quaternion
        """
        return self * quat2
    
    def conjugate(self):
        """ Return the conjugate of a quaternion as a new Quaternion """
        return Quaternion(_quat=np.append(self.quat_[0], -1 * self.quat_[1:4]))
    
    def norm(self):
        """ Return the scalar normal for a quaternion """
        return np.linalg.norm(self.quat_)
    
    def inverse(self):
        """ Return the inverse of a quaternion as a new Quaternion """
        conj = self.conjugate().quat_
        norm2 = np.square(self.norm())
        return Quaternion(_quat=(conj / norm2))
        
    def normalize(self):
        """ Return the normalized version of a quaternion as a new Quaternion.
            Note: When constructed with an arbitrary axis and angle, a
            Quaternion is already normalized by default.
        """
        return self / self.norm()

    def asTransform(self):
        """ Compute and return a rotation Transform from a quaternion.
            This produces an exact Cartesian transformation when a quaternion
            axis is aligned with a Cartesian axis.
        """
        w, x, y, z = self.quat_
        q = x * x + y * y + z * z + w * w
        s = (2.0 / q) if q > 0.0 else 0.0
        xs = x * s
        ys = y * s
        zs = z * s
        wx = w * xs
        wy = w * ys
        wz = w * zs
        xx = x * xs
        xy = x * ys
        xz = x * zs
        yy = y * ys
        yz = y * zs
        zz = z * zs

        m = np.zeros([16])

        # In Glyph order

        # If along a Cartesian axis, snap to -1, 0, and 1 if within tolerance
        if (x == 0.0 and y == 0.0) or (x == 0.0 and z == 0.0) or \
                (y == 0.0 and z == 0.0):
            m[ 0] = _clamp(1.0 - (yy + zz), 1.0, -1.0, 1e-15)
            m[ 1] = _clamp(xy + wz, 1.0, -1.0, 1e-15)
            m[ 2] = _clamp(xz - wy, 1.0, -1.0, 1e-15)
            m[ 3] = 0.0
            m[ 4] = _clamp(xy - wz, 1.0, -1.0, 1e-15)
            m[ 5] = _clamp(1.0 - (xx + zz), 1.0, -1.0, 1e-15)
            m[ 6] = _clamp(yz + wx, 1.0, -1.0, 1e-15)
            m[ 7] = 0.0
            m[ 8] = _clamp(xz + wy, 1.0, -1.0, 1e-15)
            m[ 9] = _clamp(yz - wx, 1.0, -1.0, 1e-15)
            m[10] = _clamp(1.0 - (xx + yy), 1.0, -1.0, 1e-15)
            m[11] = 0.0
            m[12] = 0.0
            m[13] = 0.0
            m[14] = 0.0
            m[15] = 1.0
        else:
            m[ 0] = 1.0 - (yy + zz)
            m[ 1] = xy + wz
            m[ 2] = xz - wy
            m[ 3] = 0.0
            m[ 4] = xy - wz
            m[ 5] = 1.0 - (xx + zz)
            m[ 6] = yz + wx
            m[ 7] = 0.0
            m[ 8] = xz + wy
            m[ 9] = yz - wx
            m[10] = 1.0 - (xx + yy)
            m[11] = 0.0
            m[12] = 0.0
            m[13] = 0.0
            m[14] = 0.0
            m[15] = 1.0

        # Python order
        m = m.reshape((4,4)).transpose()

        return Transform(m)

class Plane(object):
    """ Utility functions for infinite planes, which are represented as a list
        of four plane coefficient values.
    """
    def __init__(self, **kargs):
        if len(kargs) == 1 and 'coeffs' in kargs:
            coeffs = kargs['coeffs']
            if not isinstance(coeffs, (list, tuple)) or len(coeffs) != 4:
                raise ValueError("Coefficients must be a list of 4 values")
            self.normal_ = Vector3(coeffs[0:3]).normalize()
            self.d_ = coeffs[3]
        elif len(kargs) == 2 and set(kargs.keys()) == set(('normal', 'origin')):
            self.normal_ = Vector3(kargs['normal']).normalize()
            self.d_ = self.normal_.dot(Vector3(kargs['origin']))
        elif len(kargs) == 3 and set(kargs.keys()) == set(('p1', 'p2', 'p3')):
            v0 = Vector3(kargs['p1'])
            v1 = Vector3(kargs['p2'])
            v2 = Vector3(kargs['p3'])
            self.normal_ = (((v1 - v0).normalize()).cross(
                      (v2 - v0).normalize())).normalize()
            self.d_ = self.normal_.dot(v0)
        elif len(kargs) == 4 and set(kargs.keys()) == set(('A', 'B', 'C', 'D')):
            self.normal_ = \
                    Vector3((kargs['A'], kargs['B'], kargs['C'])).normalize()
            self.d_ = kargs['D']
        else:
            raise ValueError('Plane must be initialized with coefficient ' +
                'list, point and normal, three points (p1, p2, p3), or ' +
                'coefficients (A, B, C, D)')

    def __iter__(self):
        return (e for e in (tuple(self.normal_) + (self.d_,)))

    def __str__(self):
        """ Return the string form of a plane represented as a tuple of
            the four plane coefficients
        """
        return str(tuple(self))

    def equation(self):
        """ Return the plane equation as tuple of the four plane coefficients
        """
        return tuple(self)

    @property
    def A(self):
        """ Return the A plane coefficient """
        return self.normal_.vector_[0]

    @property
    def B(self):
        """ Return the B plane coefficient """
        return self.normal_.vector_[1]

    @property
    def C(self):
        """ Return the C plane coefficient """
        return self.normal_.vector_[2]

    @property
    def D(self):
        """ Return the D plane coefficient """
        return self.d_

    def normal(self):
        """ Return the plane normal as a tuple """
        return tuple(self.normal_)

    def constant(self):
        """ Return the scalar plane constant """
        return self.d_

    def inHalfSpace(self, vec):
        """ Check if a point is in the positive half space of a plane """
        return self.normal_.dot(Vector3(vec)) >= self.d_

    def distance(self, vec):
        """ Return the positive scalar distance of a point to a plane """
        return math.fabs(self.normal_.dot(Vector3(vec)) - self.d_)

    def line(self, origin, direction):
        """ Return the intersection of a line represented as a point and
            distance to a plane. If the line does not intersect the plane,
            an exception is raised.
        """
        if not isinstance(origin, Vector3):
            origin = Vector3(origin)
        if not isinstance(direction, Vector3):
            direction = Vector3(direction).normalize()

        den = self.normal_.dot(direction)
        if den < 1e-10 and den > -1e-10:
            raise ValueError("Line does not intersect plane")

        s = (self.d_ - self.normal_.dot(origin)) / den

        return origin + direction * s

    def segment(self, p1, p2):
        """ Return the intersection of a line represented as two points
            to a plane as a new Vector3. If the segment does not
            intersect the plane, an exception is raised.
        """
        if not isinstance(p1, Vector3):
            p1 = Vector3(p1)
        if not isinstance(p2, Vector3):
            p2 = Vector3(p2)

        ndp1 = self.normal_.dot(p1)
        ndp2 = self.normal_.dot(p2)

        if ((ndp1 < self.d_ and ndp2 < self.d_) or \
                (ndp1 > self.d_ and ndp2 > self.d_)):
            raise ValueError("Segment does not intersect plane")

        return self.line(p1, tuple(p2 - p1))

    def project(self, pt):
        """ Return the closest point projection of a point onto a plane
            as a new Vector3
        """
        if not isinstance(pt, Vector3):
            pt = Vector3(pt)
        return pt + self.normal_ * (self.d_ - pt.dot(self.normal_))


class Extents(object):
    """ Utility functions for extent boxes, which are represented as a
        list of two vectors (the min and max of the box).
    """ 
    def __init__(self, *args):
        """ Construct an extent box with the given min/max or None.
            Extents((xmin, ymin, zmin), (xmax, ymax, zmax))
            Extents(Vector3, Vector3)
            Extents(xmin, ymin, zmin, xmax, ymax, zmax)
        """
        self.box_ = None
        if len(args) == 1:
            if isinstance(args[0], Extents):
                self.box_ = args[0].box_
            else:
                self.box_ = np.array(args[0])
        elif len(args) == 2:
            if isinstance(args[0], Vector3) and isinstance(args[1], Vector3):
                self.box_ = np.array([args[0].vector_, args[1].vector_])
            elif isinstance(args[0], (list, tuple, np.ndarray)) and \
                    isinstance(args[1], (list, tuple, np.ndarray)):
                self.box_ = np.array([args[0], args[1]])
            else:
                raise ValueError("Invalid argument %s" % str(args))
        elif len(args) == 3:
            self.box_ = np.array([args, args])
        elif len(args) == 6:
            self.box_ = np.array(args)
            self.box_.shape = [2,3]
        elif len(args) != 0:
            raise ValueError("Invalid argument %s" % str(args))

        if self.box_ is not None:
            if self.box_.size == 3 and self.box_.ndim == 1:
                self.box_ = np.array([self.box_, self.box_])
            if self.box_.size != 6 or self.box_.ndim != 2:
                raise ValueError("Extent box must be 2x3 matrix")
            elif not np.less_equal(self.box_[0], self.box_[1]).all():
                raise ValueError("Min must be less than or equal to Max")

    def __repr__(self):
        return str(self.box_)

    def __iter__(self):
        if self.box_ is not None:
            return (e for e in self.box_.flatten())

    def __eq__(self, other):
        """ Check for equality of two extent boxes """
        if self.box_ is not None:
            try:
                return np.array_equal(self.box_, other.box_)
            except:
                return np.array_equal(self.box_, other)
        else:
            return False

    def minimum(self):
        """ Return the minimum corner point of an extent box """
        if self.box_ is None:
            raise ValueError("Self is empty")
        return self.box_[0]

    def maximum(self):
        """ Return the maximum corner point of an extent box """
        if self.box_ is None:
            raise ValueError("Self is empty")
        return self.box_[1]

    def isEmpty(self):
        """ Check if an extent box is empty """
        return self.box_ is None

    def diagonal(self):
        """ Return the length of the diagonal of an extent box """
        if self.box_ is not None:
            return np.linalg.norm(self.box_[0] - self.box_[1])
        else:
            return 0.0

    def enclose(self, pt):
        """ Return a new Extents that encloses the given point """
        if isinstance(pt, Vector3):
            pt = pt.vector_
        if self.box_ is None:
            return Extents([np.array(pt), np.array(pt)])
        else:
            return Extents([np.minimum(self.box_[0], pt),
                np.maximum(self.box_[1], pt)])

    def expand(self, value):
        """ Return a new Extents box that is expanded by the given amount
            at both minimum and maximum corners
        """
        return Extents([self.box_[0] - value, self.box_[1] + value])

    def isIntersecting(self, other):
        """ Return true if two extent boxes intersect or share a corner, edge
            or face
        """
        if isinstance(other, (list, tuple)):
            other = Extents(other)
        elif not isinstance(other, Extents):
            raise ValueError("Invalid argument")
        elif self.box_ is None:
            return False

        return (max(self.box_[0, 0], other.box_[0, 0]) <= \
                min(self.box_[1, 0], other.box_[1, 0])) and \
                (max(self.box_[0, 1], other.box_[0, 1]) <= \
                min(self.box_[1, 1], other.box_[1, 1])) and \
                (max(self.box_[0, 2], other.box_[0, 2]) <= \
                min(self.box_[1, 2], other.box_[1, 2]))

    def isInside(self, pt, tol=0.0):
        """ Return true if a point is within an extent box, within an
            optional tolerance
        """
        if self.box_ is None:
            return False

        pt = tuple(pt)

        return (self.box_[0, 0] + tol) <= pt[0] and \
                (self.box_[1, 0] - tol) >= pt[0] and \
                (self.box_[0, 1] + tol) <= pt[1] and \
                (self.box_[1, 1] - tol) >= pt[1] and \
                (self.box_[0, 2] + tol) <= pt[2] and \
                (self.box_[1, 2] - tol) >= pt[2]

    def translate(self, offset):
        """ Return a new Extents object that is translated by the given offset
        """
        if self.box_ is None:
            raise ValueError("Self is empty")
        elif isinstance(offset, Vector3):
            offset = tuple(offset)

        return Extents([np.add(self.box_[0], tuple(offset)),
            np.add(self.box_[1], tuple(offset))])

    def rotate(self, quat):
        """ Return a new Extents object that is rotated by the given Quaternion
        """
        if self.box_ is None:
            raise ValueError("Self is empty")
        elif not isinstance(quat, Quaternion):
            raise ValueError("quat is not a Quaternion")

        xform = quat.asTransform()
        result = Extents()

        obox = self.box_

        for i in (0,1):
            for j in (0,1):
                for k in (0,1):
                    p = xform.apply((obox[i, 0], obox[j, 1], obox[k, 2]))
                    result = result.enclose(p)

        return result

    def center(self):
        """ Return the center point of the extent box
        """
        if self.box_ is None:
            raise ValueError("Self is empty")
        return (self.box_[0] / 2.0) + (self.box_[1] / 2.0)

    def minimumSide(self):
        """ Return the length of the shortest side of the box
        """
        if self.box_ is None:
            raise ValueError("Self is empty")
        return min(self.box_[0, 0]-self.box_[1, 0],
                self.box_[0, 1]-self.box_[1, 1],
                self.box_[0, 2], self.box_[1, 2])

    def maximumSide(self):
        """ Return the length of the longest side of the box
        """
        if self.box_ is None:
            raise ValueError("Self is empty")
        return max(self.box_[0, 0]-self.box_[1, 0],
                self.box_[0, 1]-self.box_[1, 1],
                self.box_[0, 2], self.box_[1, 2])


class Transform(object):
    """ Utility functions for transform matrices, which are represented
        as a list of sixteen real values. The matrix is represented
        in a column-first order, which matches the order used in Glyph.
    """
    @staticmethod
    def identity():
        """ Return an identity Transform """
        return Transform(list(np.eye(4)))

    def __init__(self, matrix=None):
        """ Construct a Transform from an optional set of 16 real values.
            If an argument is not supplied, set to the identity matrix.
        """
        if matrix is None:
            self.xform_ = Transform.identity().xform_
            return
        elif isinstance(matrix, Quaternion):
            self.xform_ = matrix.asTransform().xform_
            return
        elif isinstance(matrix, Transform):
            self.xform_ = matrix.xform_
            return
        elif isinstance(matrix, np.matrix):
            self.xform_ = matrix.A
            return
        elif isinstance(matrix, np.ndarray):
            self.xform_ = matrix
            if matrix.size == 16:
                self.xform_ = self.xform_.reshape((4,4))
            return
        elif not isinstance(matrix, (list, tuple)):
            raise ValueError("Invalid argument")

        # Assume that the incoming transformation matrix is in Glyph order
        # (column-first), and transpose to row-first for mathematical
        # operations
        if len(matrix) == 4:
            # Assume a list/tuple of 4 lists/tuples
            self.xform_ = np.array(matrix).transpose()
        elif len(matrix) == 16:
            self.xform_ = np.array(matrix).reshape((4,4)).transpose()
        else:
            raise ValueError("Invalid xform matrix")

    def __eq__(self, other):
        """ Compare equality of two transforms """
        if isinstance(other, Transform):
            return np.array_equal(self.xform_, other.xform_)
        elif isinstance(other, (list, tuple, np.matrix, np.ndarray)):
            return np.array_equal(self.xform_, Transform(other).xform_)
        else:
            raise ValueError("Invalid argument")

    def __str__(self):
        """ Return the string representation of a Transform, as a one-
            dimensional array of floats in column-wise order
        """
        return str(tuple(self))

    def __iter__(self):
        # account for transposed glyph notation
        return (e for e in self.xform_.transpose().flatten())

    @property
    def matrix(self):
        return list(self)

    def element(self, i, j):
        """ Get an element of a transform matrix with i, j in Glyph order """
        return self.xform_.transpose()[i, j]

    @staticmethod
    def translation(offset):
        """ Return a new Transform that is a translation by the given offset """
        return Transform.identity().translate(offset)

    def translate(self, offset):
        """ Return a new Transform that adds translation to an existing
            Transform
        """
        if not isinstance(offset, Vector3):
            offset = Vector3(offset)
        col = np.dot(self.xform_, np.array(tuple(offset.vector_) + (1.0,)))
        xf = np.array(self.xform_)
        np.put(xf, [3, 7, 11, 15], col)
        return Transform(xf)

    @staticmethod
    def rotation(axis, angle, anchor=None):
        """ Return a new Transform that is a rotation by the given angle
            about the given axis at the (optional) given anchor point
        """
        return Transform.identity().rotate(axis, angle, anchor)

    def rotate(self, axis, angle, anchor=None):
        """ Return a new Transform that adds rotation to a Transform by
            the given angle about the given axis at the (optional) given
            anchor point
        """
        if not isinstance(axis, Vector3):
            axis = Vector3(axis)
        if anchor is not None:
            if not isinstance(anchor, Vector3):
                anchor = Vector3(anchor)
            axform = Transform.translation(anchor)
            axform = axform.rotate(axis, angle)
            axform = axform.translate(Vector3()-anchor)
            return Transform(np.dot(self.xform_, axform.xform_))

        # handle Cartesian rotations
        cartesian = False
        if axis.x == 0.0 and axis.y == 0.0:
            # Axis is 0 0 Z
            cartesian = True
            ct1 = 0
            ct2 = 5
            pst = 1
            nst = 4
            if axis.z > 0.0:
                angle = -angle
        elif axis.x == 0.0 and axis.z == 0.0:
            # Axis is 0 Y 0
            cartesian = True
            ct1 = 0
            ct2 = 10
            pst = 2
            nst = 8
            if axis.y < 0.0:
                angle = -angle
        elif axis.y == 0.0 and axis.z == 0.0:
            # Axis X 0 0
            cartesian = True
            ct1 = 5
            ct2 = 10
            pst = 9
            nst = 6
            if axis.x < 0.0:
                angle = -angle

        if cartesian:
            absAngle = math.fmod(math.fabs(angle), 360.0)

            if absAngle == 90.0:
                ca = 0.0
                sa = 1.0
            elif absAngle == 180.0:
                ca = -1.0
                sa = 0.0
            elif absAngle == 270.0:
                ca = 0.0
                sa = -1.0
            else:
                ca = math.cos(math.radians(absAngle))
                sa = math.sin(math.radians(absAngle))

            if angle < 0.0:
                sa = -sa

            mat = np.eye(4).flatten()
            mat[ct1] = ca
            mat[nst] = -sa
            mat[pst] = sa
            mat[ct2] = ca

            rxform = Transform(mat)
        else:
            rxform = Quaternion(axis, angle).asTransform()

        return Transform(np.dot(self.xform_, rxform.xform_))

    @staticmethod
    def scaling(scale, anchor=None):
        """ Return a new Transform that is a scale by the given factor
            (which can be a scalar or a three-dimensional vector) about
            an optional anchor point
        """
        return Transform.identity().scale(scale, anchor)

    def scale(self, scale, anchor=None):
        """ Return a new Transform that adds scaling to a Transform by
            the given factor (which can be a scalar or a three-
            dimensional vector) about an optional anchor point
        """
        if isinstance(scale, (float, int)):
            scale = ((float(scale), float(scale), float(scale)))
        else:
            scale = tuple(scale)

        if anchor is not None:
            if not isinstance(anchor, Vector3):
                anchor = Vector3(anchor)
            axform = Transform.translation(anchor)
            axform = axform.scale(scale)
            axform = axform.translate(Vector3()-anchor)
            return Transform(np.dot(self.xform_, axform.xform_))

        # transpose to make slicing easier
        xf = self.xform_.transpose()
        xf[0][0:3] = np.multiply(xf[0][0:3], scale)
        xf[1][0:3] = np.multiply(xf[1][0:3], scale)
        xf[2][0:3] = np.multiply(xf[2][0:3], scale)
        xf = xf.transpose()

        return Transform(xf)

    @staticmethod
    def calculatedScaling(anchor, start, end, tol=0.0):
        """ Return a transform matrix that scales a given point from
            one location to another anchored at a third point
        """
        if isinstance(anchor, (list, tuple)):
            anchor = Vector3(anchor)
        if isinstance(start, (list, tuple)):
            start = Vector3(start)
        if isinstance(end, (list, tuple)):
            end = Vector3(end)

        fac = Vector3()

        da0 = start - anchor
        da1 = end - anchor
        fac.x = 1.0 if math.fabs(da0.x) < tol else (da1.x / da0.x)
        fac.y = 1.0 if math.fabs(da0.y) < tol else (da1.y / da0.y)
        fac.z = 1.0 if math.fabs(da0.z) < tol else (da1.z / da0.z)

        end1 = ((start - anchor) * fac) + anchor

        da1 = end1 - anchor
        fac.x = 1.0 if math.fabs(da0.x) < tol else (da1.x / da0.x)
        fac.y = 1.0 if math.fabs(da0.y) < tol else (da1.y / da0.y)
        fac.z = 1.0 if math.fabs(da0.z) < tol else (da1.z / da0.z)

        return Transform.scaling(fac, anchor)

    @staticmethod
    def ortho(left, right, bottom, top, near, far):
        """ Return an orthonormal view Transform from a view frustum """
        if (left == right):
            raise ValueError("left and right plane constants cannot be equal")
        if (bottom == top):
            raise ValueError("bottom and top plane constants cannot be equal")
        if (near == far):
            raise ValueError("near and far plane constants cannot be equal")

        irml = 1.0 / (right - left)
        itmb = 1.0 / (top - bottom)
        ifmn = 1.0 / (far - near)

        mat = np.eye(4).flatten()

        # these are in Python order
        mat[0] = 2.0 * irml
        mat[5] = 2.0 * itmb
        mat[10] = -2.0 * ifmn
        mat[3] = -(right + left) * irml
        mat[7] = -(top + bottom) * itmb
        mat[11] = -(far + near) * ifmn

        return Transform(mat)

    @staticmethod
    def perspective(left, right, bottom, top, near, far):
        """ Return a perspective view Transform from a view frustum """
        if (left == right):
            raise ValueError("left and right plane constants cannot be equal")
        if (bottom == top):
            raise ValueError("bottom and top plane constants cannot be equal")
        if (near == far):
            raise ValueError("near and far plane constants cannot be equal")

        irml = 1.0 / (right - left)
        itmb = 1.0 / (top - bottom)
        ifmn = 1.0 / (far - near)

        mat = np.zeros([16])

        # these are in Glyph order
        mat[0] = 2.0 * near * irml
        mat[5] = 2.0 * near * itmb
        mat[8] = (right + left) * irml
        mat[9] = (top + bottom) * itmb
        mat[10] = -(far + near) * ifmn
        mat[11] = -1.0
        mat[14] = -2.0 * far * near * ifmn

        # Python order
        mat = mat.reshape((4,4)).transpose()

        return Transform(mat)

    @staticmethod
    def mirroring(normal, distance):
        """ Return a new Transform that mirrors about a plane given
            by a normal vector and a scalar distance
        """
        return Transform.identity().mirror(normal, distance)

    @staticmethod
    def mirrorPlane(plane):
        """ Return a new Transform that mirrors about a given plane """
        return Transform.identity().mirror(plane.normal_, plane.d_)

    def mirror(self, normal, distance):
        """ Return a new Transform that adds mirroring about a plane
            given by a normal vector and a scalar distance
        """
        if not isinstance(normal, Vector3):
            normal = Vector3(normal)
        normal = normal.normalize()

        # These are in Glyph order
        mat = np.zeros([16])
        mat[ 0] = 1.0 - 2.0 * normal.x * normal.x
        mat[ 1] = -2.0 * normal.y * normal.x
        mat[ 2] = -2.0 * normal.z * normal.x
        mat[ 3] = 0.0
        mat[ 4] = -2.0 * normal.x * normal.y
        mat[ 5] = 1.0 - 2.0 * normal.y * normal.y
        mat[ 6] = -2.0 * normal.z * normal.y
        mat[ 7] = 0.0
        mat[ 8] = -2.0 * normal.x * normal.z
        mat[ 9] = -2.0 * normal.y * normal.z
        mat[10] = 1.0 - 2.0 * normal.z * normal.z
        mat[11] = 0.0
        mat[12] = 2.0 * normal.x * distance
        mat[13] = 2.0 * normal.y * distance
        mat[14] = 2.0 * normal.z * distance
        mat[15] = 1.0

        # transpose back to Python order
        mat = mat.reshape((4,4)).transpose()

        return Transform(np.dot(self.xform_, mat))

    @staticmethod
    def stretching(anchor, start, end):
        """ Return a new Transform that is a stretching transform.
            If the vector defined by the start and end points is
            orthogonal to the vector defined by the start and anchor
            points, the transform is undefined and the matrix will
            be set to the identity matrix.
        """
        return Transform.identity().stretch(anchor, start, end)

    def stretch(self, anchor, start, end):
        """ Return a new Transform that adds stretching to a Transform.
            If the vector defined by the start and end points is
            orthogonal to the vector defined by the start and anchor
            points, the transform is undefined and the matrix will
            be set to the identity matrix.
        """
        if not isinstance(anchor, Vector3):
            anchor = Vector3(anchor)
        if not isinstance(start, Vector3):
            start = Vector3(start)
        if not isinstance(end, Vector3):
            end = Vector3(end)

        aToStart = start - anchor
        aToEnd = end - anchor

        sDir = (end - start).normalize()

        if math.fabs(aToStart.normalize().dot(sDir)) >= 0.01:
            factor = (aToEnd.dot(sDir) / aToStart.dot(sDir)) - 1.0
            # These are in Glyph order
            mat = np.eye(4).flatten()
            mat[ 0] = factor * sDir.x * sDir.x
            mat[ 1] = factor * sDir.y * sDir.x
            mat[ 2] = factor * sDir.z * sDir.x
            mat[ 4] = factor * sDir.x * sDir.y
            mat[ 5] = factor * sDir.y * sDir.y
            mat[ 6] = factor * sDir.z * sDir.y
            mat[ 8] = factor * sDir.x * sDir.z
            mat[ 9] = factor * sDir.y * sDir.z
            mat[10] = factor * sDir.z * sDir.z

            # transpose back to Python order to apply translation
            mat = mat.reshape((4,4)).transpose()

            axform = Transform.translation(Vector3()-anchor)
            mat = np.dot(mat, axform.xform_)
            axform = Transform.translation(anchor)
            mat = np.dot(axform.xform_, mat)

            # Glyph order
            mat = mat.transpose().flatten()
            # mat = np.ravel(mat)
            mat[ 0] += 1.0
            mat[ 5] += 1.0
            mat[10] += 1.0
            mat[12] -= anchor.x
            mat[13] -= anchor.y
            mat[14] -= anchor.z

            # Python order
            mat = mat.reshape((4,4)).transpose()

            return Transform(np.dot(self.xform_, mat))
        else:
            return Transform(self.xform_)
                
    def apply(self, vec):
        """ Return a new Vector3 that is transformed from a given point """
        # apply transform to a point
        if not isinstance(vec, Vector3):
            vec = Vector3(vec)
        rw = np.array(tuple(vec.vector_) + (1.0,))
        rw = np.dot(self.xform_, rw)
        vec = np.array(rw[0:3])
        if rw[3] != 0.0:
            vec = vec / rw[3]
        return Vector3(vec)

    def applyToDirection(self, direct):
        """ Return a a new Vector3 that is a transformed direction vector.

            This differs from apply as follows:
            
            When transforming a point by a 4x4 matrix, the point is
            represented by a vector with X, Y, and Z as the first 3
            components and 1 as the fourth component.  This allows
            the point to pick up any translation component in the matrix.
            This method represents the direction as a vector with 0 as
            the fourth component.  Since a direction can be thought of
            as the difference between two points, a zero fourth component
            is the difference between two points that have 1 as the fourth
            component.
        """
        # apply transform to a direction vector, as opposed to a point
        if not isinstance(direct, Vector3):
            direct = Vector3(direct)
        rw = np.array(tuple(direct.vector_) + (0.0,))
        rw = np.dot(self.xform_, rw)
        direct = np.array(rw[0:3])
        if rw[3] != 0.0:
            direct = direct / rw[3]
        return Vector3(direct)

    def applyToNormal(self, normal):
        """ Return a new Vector3 that is a transformed normal vector.
            A normal vector is transformed by multiplying the normal
            by the transposed inverse matrix.
        """
        if not isinstance(normal, Vector3):
            normal = Vector3(normal)
        rw = np.array(tuple(normal.vector_) + (0.0,))
        rw = np.dot(np.linalg.inv(self.xform_).transpose(), rw)
        normal = np.array(rw[0:3])
        return Vector3(normal).normalize()

    def applyToPlane(self, plane):
        """ Return a new Plane that is transformed plane """
        o = self.apply(plane.project((0, 0, 0)))
        n = self.applyToNormal(plane.normal_)
        return Plane(origin=o, normal=n)

    def __mul__(self, other):
        """ Return a the multiplication of self and either another Transform
            (a new Transform) or a Vector3 (a new, transformed Vector3)
        """
        if isinstance(other, Vector3):
            return self.apply(other)
        elif isinstance(other, Transform):
            return Transform(np.dot(self.xform_, other.xform_))
        else:
            raise ValueError("Invalid argument")

    def multiply(self, other):
        """ Return a new Transform that is the multiplication of self
            and another Transform. This is equivalent to 'self * other'.
        """
        if isinstance(other, Transform):
            return self * other
        else:
            raise ValueError("Invalid argument")

    def determinant(self):
        """ Return the scalar determinant of the transformation matrix """
        return np.linalg.det(self.xform_)

    def transpose(self):
        return Transform(self.xform_.transpose())

    def inverse(self):
        return Transform(np.linalg.inv(self.xform_))

def _clamp(v, high, low, tol=0.0):
    """ Clamp a value to a range, or zero if within tolerance """
    if v > high-tol:
        return high
    elif v < low+tol:
        return low
    elif v > -tol and v < tol:
        return 0.0
    else:
        return v

#############################################################################
#
# This file is licensed under the Cadence Public License Version 1.0 (the
# "License"), a copy of which is found in the included file named "LICENSE",
# and is distributed "AS IS." TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE
# LAW, CADENCE DISCLAIMS ALL WARRANTIES AND IN NO EVENT SHALL BE LIABLE TO
# ANY PARTY FOR ANY DAMAGES ARISING OUT OF OR RELATING TO USE OF THIS FILE.
# Please see the License for the full text of applicable terms.
#
#############################################################################
