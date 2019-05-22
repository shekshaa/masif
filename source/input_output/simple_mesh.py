# Simple ply loading class. 
# I created this class to avoid the need to install pymesh if the only goal is to load ply files. 
# Use this only for the pymol plugin. Currently only supports ascii ply files.
# Pablo Gainza LPDI EPFL 2019
import numpy as np
class Simple_mesh:

    def __init__(self, vertices=[], faces=[]):
        self.faces = faces
        self.attributes = {}
        self.vertices = []
        self.attribute_names = []
        if len(vertices) > 0:
            self.vertices = np.array(vertices)
            self.set_attribute('vertex_x', self.vertices[:,0])
            self.set_attribute('vertex_y', self.vertices[:,1])
            self.set_attribute('vertex_z', self.vertices[:,2])
            self.set_attribute('vertex_charge', np.zeros(len(vertices)))

    def load_mesh(self, filename):
        lines = open(filename, 'r').readlines()
        # Read header
        self.attribute_names = []
        self.num_verts = 0
        line_ix = 0
        while 'end_header' not in lines[line_ix]: 
            line = lines[line_ix]
            if line.startswith('element vertex'): 
                self.num_verts = int(line.split(' ')[2])
            if line.startswith('property float'):
                self.attribute_names.append('vertex_'+line.split(' ')[2].rstrip())
            if line.startswith('element face'):
                self.num_faces= int(line.split(' ')[2])
            line_ix += 1
        line_ix += 1
        header_lines = line_ix
        self.attributes = {}
        for at in self.attribute_names:
            self.attributes[at] = []
        self.vertices = []
        self.normals = []
        self.faces = []
        # Read vertex attributes.
        for i in range(header_lines, self.num_verts+header_lines):
            cur_line = lines[i].split(' ')
            vert_att = [float(x) for x in cur_line]
            # Organize by attributes
            for jj, att in enumerate(vert_att): 
                self.attributes[self.attribute_names[jj]].append(att)
            line_ix += 1
        # Set up vertices
        for jj in range(len(self.attributes['vertex_x'])):
            self.vertices = np.vstack([self.attributes['vertex_x'],\
                                    self.attributes['vertex_y'],\
                                    self.attributes['vertex_z']]).T
        # Read faces.
        face_line_start = line_ix
        for i in range(face_line_start, face_line_start+self.num_faces):
            try:
                fields = lines[i].split(' ')
            except:
                ipdb.set_trace()
            face = [int(x) for x in fields[1:]]
            self.faces.append(face)
        self.faces = np.array(self.faces)
        self.vertices = np.array(self.vertices)
        # Convert to numpy array all attributes.
        for key in self.attributes.keys():
            self.attributes[key] = np.array(self.attributes[key])

    def set_attribute(self, attribute_name, vals):
        if attribute_name not in self.attribute_names:
            self.attribute_names.append(attribute_name)
        self.attributes[attribute_name] = vals

    def get_attribute_names(self):
        return list(self.attribute_names)

    def get_attribute(self, attribute_name):
        return np.copy(self.attributes[attribute_name])

    def save_mesh(self, filename):
        outstring = 'ply\n'+\
                    'format ascii 1.0\n'+\
                    'comment Generated by MaSIF\n'
                    
        outstring += 'element vertex {}\n'.format(len(self.vertices))
        for attribute in self.attribute_names: 
            if attribute.startswith('vertex'):
                att = attribute.split('_')[1]
                outstring += 'property float {}\n'.format(att)
        outstring += 'element face {}\n'.format(len(self.faces))
        outstring += 'property list uchar int vertex_indices\n'
        outstring += 'end_header\n'
        for ix, vert in enumerate(self.vertices):
            # Assume that the three first attributes are x, y, z
            outstring += '{:.2f} {:.2f} {:.2f}'.format(vert[0], vert[1], vert[2])
            for att in self.attribute_names[3:]:
                outstring += ' {:.2f}'.format(self.attributes[att][ix])
            outstring += '\n'
        for f in self.faces: 
            outstring += '3 {} {} {}\n'.format(f[0], f[1], f[2])
        outfile = open(filename, 'w+')
        outfile.write(outstring)
        outfile.close()



