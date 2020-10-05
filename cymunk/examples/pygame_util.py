# ----------------------------------------------------------------------------
# cymunk
# Copyright (c) 2007-2012 Victor Blomqvist
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------

"""This submodule contains helper functions to help with quick prototyping 
using cymunk together with pygame.

Intended to help with debugging and prototyping, not for actual production use
in a full application. The methods contained in this module is opinionated 
about your coordinate system and not in any way optimized. 
"""

__version__ = "$Id$"
__docformat__ = "reStructuredText"

__all__ = ["draw", "get_mouse_pos", "to_pygame", "from_pygame"]

import pygame

import cymunk
from cymunk import Vec2d

flip_y = True
"""Flip the y cooridnate to make y point upwards"""

def draw(surface, *objs):
    """Draw one or many cymunk objects on a pygame.Surface object.
        
    This method currently supports drawing of
        * cymunk.Space
        * cymunk.Segment
        * cymunk.Circle
        * cymunk.Poly
        * cymunk.Constraint objects 

    If a Space is passed in all shapes in that space will be drawn. 
    Unrecognized objects will be ignored (for example if you pass in a 
    constraint).
    
    Typical usage::
    
    >>> cymunk.pygame_util.draw(screen, my_space)
        
    You can control the color of a shape by setting shape.color to the color 
    you want it drawn in.
    
    >>> my_shape.color = pygame.color.THECOLORS["pink"]
    
    If you do not want a shape to be drawn, set shape.ignore_draw to True.
    
    >>> my_shape.ignore_draw = True
        
    Not all constraints are currently drawn in a very clear way, but all the 
    different shapes should look fine both as static and dynamic objects.
    
    See pygame_util.demo.py for a full example
    
    :Parameters:
            surface : pygame.Surface
                Surface that the objects will be drawn on
            objs : One or many objects to draw
                Can be either a single object or a list like container with 
                objects.
    """
    
    for o in objs:
        if isinstance(o, cymunk.Space):
            _draw_space(surface, o)
        elif isinstance(o, cymunk.Shape):
            _draw_shape(surface, o)
        elif isinstance(o, cymunk.Constraint):
            _draw_constraint(surface, o)
        elif hasattr(o, '__iter__'):
            for oo in o:
                draw(surface, oo)
                
def _draw_space(surface, space):
    
    (width, height) = surface.get_size()
    
    for s in space.shapes.itervalues():
        if not (hasattr(s, "ignore_draw") and s.ignore_draw):
            _draw_shape(surface, s)
            
    for c in space.constraints:
        if not (hasattr(c, "ignore_draw") and c.ignore_draw):
            _draw_constraint(surface, c)

def _draw_shape(surface, shape):
    
    if isinstance(shape, cymunk.Circle):
        _draw_circle(surface, shape)
    elif isinstance(shape, cymunk.Segment):
        _draw_segment(surface, shape)
    elif  isinstance(shape, cymunk.Poly):
        _draw_poly(surface, shape)
        
def _draw_circle(surface, circle):
    
    circle_center = circle.body.position + circle.offset.rotated(circle.body.angle)
    p = to_pygame(circle_center, surface)
   
    r = 0
    color = pygame.color.THECOLORS["red"]
    if circle.body.is_static:
        color = pygame.color.THECOLORS["lightgrey"]
        r = 1
    if hasattr(circle, "color"):
        color = circle.color  
        
    pygame.draw.circle(surface, color, p, int(circle.radius), r)
    
    circle_edge = circle_center + Vec2d(circle.radius, 0).rotated(circle.body.angle)
    p2 = to_pygame(circle_edge, surface)
    line_r = 3 if circle.radius > 20 else 1
    pygame.draw.lines(surface, pygame.color.THECOLORS["blue"], False, [p,p2], line_r)

def _draw_poly(surface, poly):
    
    ps = poly.get_vertices()
    ps = [to_pygame(p, surface) for p in ps]
    ps += [ps[0]]
    if hasattr(poly, "color"):
        color = poly.color  
    elif poly.body.is_static:
        color = pygame.color.THECOLORS["lightgrey"]
    else:
        color = pygame.color.THECOLORS["green"]
    pygame.draw.lines(surface, color, False, ps, 1)#max(int(poly.radius*2),1))

def _draw_segment(surface, segment):
    
    body = segment.body
    pv1 = body.position + segment.a.rotated(body.angle)
    pv2 = body.position + segment.b.rotated(body.angle)

    p1 = to_pygame(pv1, surface)
    p2 = to_pygame(pv2, surface)
    
    if hasattr(segment, "color"):
        color = segment.color  
    elif segment.body.is_static:
        color = pygame.color.THECOLORS["lightgrey"]
    else:
        color = pygame.color.THECOLORS["blue"]
    pygame.draw.lines(surface, color, False, [p1,p2], max(int(segment.radius*2),1))
    
def _draw_constraint(surface, constraint):
    
    if isinstance(constraint, cymunk.GrooveJoint) and hasattr(constraint, "groove_a"):
        pv1 = constraint.a.position + constraint.groove_a.rotated(constraint.a.angle)
        pv2 = constraint.a.position + constraint.groove_b.rotated(constraint.a.angle)
        p1 = to_pygame(pv1, surface)
        p2 = to_pygame(pv2, surface)
        pygame.draw.aalines(surface, pygame.color.THECOLORS["darkgray"], False, [p1,p2])
    elif isinstance(constraint, cymunk.PinJoint):
        pv1 = constraint.a.position + constraint.anchr1.rotated(constraint.a.angle)
        pv2 = constraint.b.position + constraint.anchr2.rotated(constraint.b.angle)
        p1 = to_pygame(pv1, surface)
        p2 = to_pygame(pv2, surface)
        pygame.draw.aalines(surface, pygame.color.THECOLORS["darkgray"], False, [p1,p2])    
    elif isinstance(constraint, cymunk.GearJoint):
        pv1 = constraint.a.position
        pv2 = constraint.a.position
        p1 = to_pygame(pv1, surface)
        p2 = to_pygame(pv2, surface)
        pygame.draw.circle(surface, pygame.color.THECOLORS["darkgray"], p1, 3)
        pygame.draw.circle(surface, pygame.color.THECOLORS["darkgray"], p2, 3)
    elif hasattr(constraint, "anchr1"):
        pv1 = constraint.a.position + constraint.anchr1.rotated(constraint.a.angle)
        pv2 = constraint.b.position + constraint.anchr2.rotated(constraint.b.angle)
        p1 = to_pygame(pv1, surface)
        p2 = to_pygame(pv2, surface)
        pygame.draw.aalines(surface, pygame.color.THECOLORS["darkgray"], False, [p1,p2])
    else:
        pv1 = constraint.a.position
        pv2 = constraint.b.position
        p1 = to_pygame(pv1, surface)
        p2 = to_pygame(pv2, surface)
        pygame.draw.aalines(surface, pygame.color.THECOLORS["darkgray"], False, [p1,p2])    

def get_mouse_pos(surface):
    """Get position of the mouse pointer in cymunk coordinates."""
    p = pygame.mouse.get_pos()
    return from_pygame(p, surface)

def to_pygame(p, surface):
    """Convenience method to convert cymunk coordinates to pygame surface 
    local coordinates
    """
    if flip_y:
        return int(p[0]), surface.get_height()-int(p[1])
    else:
        return int(p[0]), int(p[1])
    
def from_pygame(p, surface):
    """Convenience method to convert pygame surface local coordinates to 
    cymunk coordinates    
    """
    return to_pygame(p,surface)

            
