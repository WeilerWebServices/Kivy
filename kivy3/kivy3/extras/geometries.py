"""
The MIT License (MIT)

Copyright (c) 2013 Niko Skrypnik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from kivy3 import Vector3
from kivy3.core.geometry import Geometry
from kivy3.core.face3 import Face3

import math


def normalise_v3(vector):
    length= math.sqrt(vector[
    0]**2 + vector[1]**2 + vector[2]**2)
    new_vector = [x/length for x in vector]
    return new_vector

class BoxGeometry(Geometry):

    _cube_vertices = [(-1, 1, -1), (1, 1, -1),
                      (1, -1, -1), (-1, -1, -1),
                      (-1, 1, 1), (1, 1, 1),
                      (1, -1, 1), (-1, -1, 1),
                      ]

    _cube_faces = [(0, 1, 2), (0, 2, 3), (3, 2, 6),
                   (3, 6, 7), (7, 6, 5), (7, 5, 4),
                   (4, 5, 1), (4, 1, 0), (4, 0, 3),
                   (7, 4, 3), (5, 1, 2), (6, 5, 2)
                   ]

    _cube_normals = [(0, 0, 1), (-1, 0, 0), (0, 0, -1),
                     (1, 0, 0), (0, 1, 0), (0, -1, 0)
                     ]

    def __init__(self, width, height, depth, **kw):
        name = kw.pop('name', '')
        super(BoxGeometry, self).__init__(name)
        self.width_segment = kw.pop('width_segment', 1)
        self.height_segment = kw.pop('height_segment', 1)
        self.depth_segment = kw.pop('depth_segment', 1)

        self.w = width
        self.h = height
        self.d = depth

        self._build_box()

    def _build_box(self):

        for v in self._cube_vertices:
            v = Vector3(0.5 * v[0] * self.w,
                        0.5 * v[1] * self.h,
                        0.5 * v[2] * self.d)
            self.vertices.append(v)

        n_idx = 0
        for f in self._cube_faces:
            face3 = Face3(*f)
            normal = self._cube_normals[int(n_idx / 2)]
            face3.vertex_normals = [normal, normal, normal]
            n_idx += 1
            self.faces.append(face3)

class CylinderGeometry(Geometry):
    def __init__(self, radius, length, **kw):
        name = kw.pop('name', '')
        super(CylinderGeometry, self).__init__(name)
        self.circle_segment = kw.pop('circle_segment', 16)
        self.depth_segment = kw.pop('depth_segment', 1)

        self.rad = radius
        self.length = length

        self._build_cylinder()

    def _build_cylinder(self):

        _cylinder_vertices = []
        top_vertices = []
        bottom_vertices = []
        cylinder_side_normals = []
        _cylinder_normals = []

        for i in range(self.circle_segment):
            x = math.cos(float(i) * (2.*math.pi)/float(self.circle_segment)) * 0.5 * float(self.rad)
            y = math.sin(float(i) * (2.*math.pi)/float(self.circle_segment)) * 0.5 * float(self.rad)

            n = Vector3(x,y,0)
            n.normalize()
            cylinder_side_normals.append(n)



            top_vertices.append((x,y,0.5 * float(self.length)))
            bottom_vertices.append((x,y,-0.5 * float(self.length)))

        _cylinder_vertices = top_vertices + bottom_vertices
        _cylinder_normals = cylinder_side_normals + cylinder_side_normals

        for f in range(1,self.circle_segment-1):
            # Top circle
            normal = Vector3(0,0,1)
            face = (0,f,f+1)
            face3 = Face3(*face)
            face3.vertex_normals=[normal,normal,normal]
            self.faces.append(face3)

        for f in range(self.circle_segment+1,(2*self.circle_segment)-1):
            # Top circle
            normal = Vector3(0,0,-1)
            face = (self.circle_segment,f,f+1)
            face3 = Face3(*face)
            face3.vertex_normals=[normal,normal,normal]
            self.faces.append(face3)


        for i in range(0,self.circle_segment):
            if i == (self.circle_segment-1):
                face = (i,0,i+self.circle_segment)
            else:
                face = (i,i+1,i+self.circle_segment)
            face3 = Face3(*face)
            face3.vertex_normals = [_cylinder_normals[i], _cylinder_normals[i+1], _cylinder_normals[i+self.circle_segment]]
            self.faces.append(face3)

            if i == (self.circle_segment-1):
                face = (0, i+self.circle_segment, self.circle_segment)
                face3=Face3(*face)
                face3.vertex_normals=(_cylinder_normals[i+1], _cylinder_normals[i+self.circle_segment], _cylinder_normals[self.circle_segment])
            else:
                face = (i+1, i+self.circle_segment, i+self.circle_segment +1)

                face3=Face3(*face)
                face3.vertex_normals=(_cylinder_normals[i+1], _cylinder_normals[i+self.circle_segment], _cylinder_normals[i+self.circle_segment + 1])
            self.faces.append(face3)


        self.vertices = _cylinder_vertices


class SphereGeometry(Geometry):

    def __init__(self, radius=1, sectors=36, stacks=18, **kw):
        name = kw.pop('name', '')
        super(SphereGeometry, self).__init__(name)
        self.stacks = stacks
        self.sectors=sectors
        self.rad = radius

        self._build_sphere()

    def _build_sphere(self):
        #Create Vertices and normals
        _vertices = []
        _normals = []
        #Top vertex
        _vertices.append((0,0,1.*self.rad))
        _normals.append((0,0,1))

        # Generate the faces
        for i in range(1,self.stacks):
            theta_1 = float(i)*(math.pi/self.stacks)
            z = math.cos(theta_1)
            for j in range(self.sectors):
                theta_2 = float(j)*(2.*math.pi/self.sectors)
                x = math.sin(theta_1) * math.cos(theta_2)
                y = math.sin(theta_1) * math.sin(theta_2)

                vertex = (x*self.rad, y*self.rad, z*self.rad)
                _vertices.append(vertex)
                _normals.append((x,y,z))

        # Bottom vertex
        _vertices.append((0,0,-1.*self.rad))
        _normals.append((0,0,-1.))

        # Generate the Faces with mapping to the vertices

        #Top one
        for i in range(1,self.sectors+1):

            a = 0
            b = i
            c = i+1
            if c == self.sectors+1:
                c = 1
            face3=Face3(a, b, c)
            face3.vertex_normals=[_normals[a],_normals[b],_normals[c]]
            self.faces.append(face3)

        #Stacks:
        for i in range(0, self.stacks-2):
            top_idx = (i*self.sectors +1, (i+1)*self.sectors+1)
            for j in range(top_idx[0],top_idx[1]):
                a = j
                b = j+1
                c = j+self.sectors
                if b == top_idx[1]:
                    b = top_idx[0]
                face3=Face3(a, b, c)
                face3.vertex_normals = [_normals[a],_normals[b],_normals[c]]
                self.faces.append(face3)

                a = j+1
                b = j+self.sectors
                c = j+self.sectors +1
                if a == top_idx[1]:
                    a = top_idx[0]
                if c == top_idx[1] + self.sectors:
                    c = top_idx[1]

                face3=Face3(a, b, c)
                face3.vertex_normals = [_normals[a],_normals[b],_normals[c]]
                self.faces.append(face3)

        for i in range(len(_vertices)-1-self.sectors,len(_vertices)-1):

            a = len(_vertices)-1
            b = i
            c = i+1
            if c ==len(_vertices)-1:
                c = len(_vertices)-1-self.sectors
            face3=Face3(a, b, c)
            face3.vertex_normals=[_normals[a],_normals[b],_normals[c]]
            self.faces.append(face3)

        self.vertices = _vertices
