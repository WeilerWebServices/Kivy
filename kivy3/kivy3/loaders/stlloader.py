from .loader import BaseLoader
from os.path import abspath, dirname, join, exists
from kivy.core.image import Image
from kivy.graphics import Mesh as KivyMesh
from kivy.logger import Logger
from kivy3 import Object3D, Mesh, Material, Vector2
from kivy3.core.geometry import Geometry
from kivy3.core.face3 import Face3
import numpy as np
from stl import mesh

DEFAULT_VERTEX_FORMAT = [
    (b'v_pos', 3, 'float'),
    (b'v_normal', 3, 'float'),
    (b'v_tc0', 2, 'float')
]
DEFAULT_MESH_MODE = 'triangles'

class STLMesh(Object3D):
    def __init__(self, v0, v1, v2, normals, material, **kw):
        super(STLMesh, self).__init__(**kw)
        self.vertex_format = kw.pop('vertex_format', DEFAULT_VERTEX_FORMAT)
        self.mesh_mode = kw.pop('mesh_mode', DEFAULT_MESH_MODE)
        self.material = material
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.normals = normals
        indices = list(range(0,len(self.v0)*3))
        uvs = np.zeros((len(self.v0), 2)).astype(np.float32)
        vertices = np.block([self.v0,self.normals,uvs,self.v1,self.normals,uvs,self.v2,self.normals,uvs]).flatten()

        kw=dict(vertices=vertices,
                indices=indices,
                fmt=self.vertex_format,
                mode=self.mesh_mode)

        if self.material.map:
            kw['texture'] = self.material.map
        self._mesh = KivyMesh(**kw)


class STLObject(Object3D):
    def __init__(self, stl_mesh, material, **kw):
        super(STLObject, self).__init__(**kw)
        self.stl_mesh = stl_mesh
        self.material = material
        self.mtl = self.material  # shortcut for material property

        self.create_mesh()

    def create_mesh(self):
        """ Create real mesh object from the geometry and material """
        max_faces = 65530//3
        #geometries = []
        start = 0

        while(True):
            _faces=[]
            _vertices = []
            if (len(self.stl_mesh.v0)-start) >= max_faces:
                print("Faces are more than max")
                length = max_faces
                #
                # mesh = STLMesh(self.stl_mesh.v0[start:start+length], self.stl_mesh.v1[start:start+length], self.stl_mesh.v2[start:start+length], self.stl_mesh.normals[start:start+length],
                # self.material)
                #
                # self.add(mesh)
                _vertices = np.concatenate((self.stl_mesh.v0[start:start+length],self.stl_mesh.v1[start:start+length],self.stl_mesh.v2[start:start+length]))
                for i in range(length):

                    f3 = Face3(i,i+length, i+ length*2)
                    f3.vertex_normals = [self.stl_mesh.normals[start+i],self.stl_mesh.normals[start+i],self.stl_mesh.normals[start+i]]
                    _faces.append(f3)



                geo = Geometry()
                geo.vertices = _vertices
                geo.faces = _faces
                mesh = Mesh(geo, self.material)
                self.add(mesh)
                start = start+length


            else:
                length = len(self.stl_mesh.v0)-start
                _vertices = np.concatenate((self.stl_mesh.v0[start:],self.stl_mesh.v1[start:],self.stl_mesh.v2[start:]))
                for i in range(length):
                    f3 = Face3(i,i+length, i+ length*2)
                    f3.vertex_normals = [self.stl_mesh.normals[i+start],self.stl_mesh.normals[i+start],self.stl_mesh.normals[i+start]]
                    _faces.append(f3)
                geo = Geometry()
                geo.vertices = _vertices
                geo.faces = _faces
                #geometries.append(geo)
                mesh = Mesh(geo, self.material)
                self.add(mesh)

                # length = max_faces
                #
                # mesh = STLMesh(self.stl_mesh.v0[start:], self.stl_mesh.v1[start:], self.stl_mesh.v2[start:], self.stl_mesh.normals[start:],
                # self.material)
                #
                # self.add(mesh)
                break

        return self




class STLLoader(BaseLoader):
    def __init__(self, **kw):
        super(STLLoader, self).__init__(**kw)

    def load(self, source, material, **kw):
        self.material = material
        return super(STLLoader, self).load(source, **kw)


    def parse(self):

        stl = mesh.Mesh.from_file(self.source)



        stl_object = STLObject(stl,self.material)



        return stl_object
