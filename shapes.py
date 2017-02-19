import tkinter
import math
from math import sin, cos
from random import randrange as r
from typing import List, Tuple

Vec3D = Tuple[float, float, float]

class Shape3D:
    """A class for representing 3D shapes.

    The x-axis goes through the screen, with the positive end infront of the screen and the negative end behind.
    The y-axis is horizontal, with the negative end being the left side of the screen and the positive end on the right.
    The z-axis is vertical, the the negative end at the bottom of the screen and the positive end at the top.
    """
    def __init__(self, points: List[float]):
        assert len(points)%3 == 0
        self.points = points

    def rotate(self, angle: float, direction: Vec3D, point: Vec3D):
        """Rotates the points of the Shape around the axis given by the point and direction."""
        #http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/
        points = self.points

        a = point[0]
        b = point[1]
        c = point[2]
        
        u = direction[0]
        v = direction[1]
        w = direction[2]

        s = sin(angle)
        c0 = cos(angle)
        c1 = 1 - c0

        u2 = u*u
        v2 = v*v
        w2 = w*w

        x1 = c1*(a*(v2 + w2) - u*(b*v + c*w)) + s*(b*w - c*v)
        x2 = u*c1
        y1 = c1*(b*(w2 + u2) - v*(c*w + a*u)) + s*(c*u - a*w)
        y2 = v*c1
        z1 = c1*(c*(u2 + v2) - w*(a*u + b*v)) + s*(a*v - b*u)
        z2 = w*c1

        for i in range(0, len(points), 3):
            x  = points[i]
            y = points[i + 1]
            z = points[i + 2]
            dotp = u*x + v*y + w*z
            points[i] = x1 + x2*dotp + x*c0 + s*(v*z - w*y)
            points[i + 1] = y1 + y2*dotp + y*c0 + s*(w*x - u*z)
            points[i + 2] = z1 + z2*dotp + z*c0 + s*(u*y - v*x)


    def apply_perspective(self, camera_pos: Vec3D, viewer_pos: Vec3D) -> List[float]:
        """Creates an array of perspective projected (onto the y/z plane) points."""
        #http://en.wikipedia.org/wiki/3D_projection#Perspective_projection
        points = self.points
        projected = (2*len(points)//3) * [0]
        ptr = 0
        a, b, c = viewer_pos
        d, e, f = camera_pos
        for i in range(0, len(points), 3):
            x = points[i] - d
            y = points[i + 1] - e
            z = points[i + 2] - f
            projected[ptr] = b - a*y/x
            projected[ptr + 1] = c - a*z/x
            ptr += 2
        return projected


class Cube(Shape3D):
    def __init__(self, front_right_top: Vec3D, side_length: float):
        x, y, z = front_right_top
        xs, ys, zs = x - side_length, y - side_length, z - side_length
        super().__init__([
                x, y, z,
                x, y, zs,
                x, ys, zs,
                x, ys, z,
                xs, ys, z,
                xs, ys, zs,
                xs, y, zs,
                xs, y, z])
        self.colors = ['#%2X%2X%2X' % (r(256), r(256), r(256)) for i in range(6)]
        self.side_length = side_length
        
    def draw(self, camera: Vec3D, viewer: Vec3D, canvas: tkinter.Canvas, width: int, height: int) -> List[int]:
        points = self.points
        colors = self.colors
        hw = width//2
        hh = height//2

        a = camera[0]
        b = camera[1]
        c = camera[2]

        faces = [[0, 2, 4, 6],
                 [0, 14, 8, 6],
                 [0, 2, 12, 14],
                 [4, 10, 8, 6],
                 [2, 4, 10, 12],
                 [10, 12, 14, 8]]

        face_indices = [0, 1, 2, 3, 4, 5]
        
        distances = [0]*8
        distances[0] = ((a - points[0])**2 + (b - points[1])**2 + (c - points[2])**2)**0.5
        distances[1] = ((a - points[3])**2 + (b - points[4])**2 + (c - points[5])**2)**0.5
        distances[2] = ((a - points[6])**2 + (b - points[7])**2 + (c - points[8])**2)**0.5
        distances[3] = ((a - points[9])**2 + (b - points[10])**2 + (c - points[11])**2)**0.5
        distances[4] = ((a - points[12])**2 + (b - points[13])**2 + (c - points[14])**2)**0.5
        distances[5] = ((a - points[15])**2 + (b - points[16])**2 + (c - points[17])**2)**0.5
        distances[6] = ((a - points[18])**2 + (b - points[19])**2 + (c - points[20])**2)**0.5
        distances[7] = ((a - points[21])**2 + (b - points[22])**2 + (c - points[23])**2)**0.5

        def key(i):
            return (distances[faces[i][0]//2] +
                    distances[faces[i][1]//2] +
                    distances[faces[i][2]//2] +
                    distances[faces[i][3]//2])/4

        # sort the faces of the cube by the average distance of their vertices from the camera.
        # those furthest from the camera are drawn first, which is why reverse=True.
        face_indices.sort(key=key, reverse=True)

        ppoints = self.apply_perspective(camera, viewer)

        polygons = [0]*6
        for i in face_indices:
            color = colors[i]
            face = faces[i]
            polygons[i] = canvas.create_polygon(hw + ppoints[face[0]], hh - ppoints[face[0]+1],
                                                hw + ppoints[face[1]], hh - ppoints[face[1]+1],
                                                hw + ppoints[face[2]], hh - ppoints[face[2]+1],
                                                hw + ppoints[face[3]], hh - ppoints[face[3]+1],
                                                fill=color)
        return polygons
    
class Animation:
    def __init__(self, width: int = 1280, height: int = 720, max_fps: float = 60.0,
                 rotation_speed: float = 2*math.pi/3, camera: Vec3D = (500.0,0.0,0.0),
                 viewer: Vec3D = (550.0,0.0,0.0), axis: Vec3D  = (3**0.5/3,3**0.5/3,3**0.5/3),
                 point: Vec3D = (0.0,0.0,0.0)):
        self.frame_delay = int(1000/max_fps) # milliseconds between frames
        self.angle_delta = rotation_speed*self.frame_delay/1000
        self.camera = camera
        self.viewer = viewer
        self.axis = axis
        self.point = point
        self.width = width
        self.height = height
        self.master = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.master, width=width, height=height)
        self.canvas.pack()
        self.shapes = []  # type: List[Shape3D]
        self.master.after(0, self._animate)

    def add_shape(self, shape: Shape3D):
        self.shapes.append(shape)

    def _animate(self):
        angle = self.angle_delta
        direction = self.axis
        point = self.point
        canvas = self.canvas
        camera = self.camera
        viewer = self.viewer
        width = self.width
        height = self.height

        canvas.delete('all')
        for shape in self.shapes:
            shape.rotate(angle, direction, point)
            shape.draw(camera, viewer, canvas, width, height)

        self.master.update_idletasks()
        self.master.after(self.frame_delay, self._animate)
        

    def run(self):
        self.master.mainloop()

if __name__ == '__main__':
    cube = Cube((100.0,100.0,100.0), 200.0)
    animation = Animation()
    animation.add_shape(cube)
    animation.run()
