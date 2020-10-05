import cymunk as cy
import pytest

def test_space_attributes():
    space = cy.Space()
    assert(space is not None)

    assert(space.iterations == 10)
    space.iterations = 20
    assert(space.iterations == 20)

    assert(len(space.bodies) == 0)
    assert(len(space.static_shapes) == 0)
    assert(len(space.bodies) == 0)
    assert(len(space.constraints) == 0)
    assert(space.static_body is not None)
    assert(isinstance(space.static_body, cy.Body))
    assert(space.damping == 1.)
    assert(space.idle_speed_threshold == 0.)
    assert(space.sleep_time_threshold == float('inf'))
    assert(space.collision_slop < 0.2)
    assert(space.collision_bias < 0.01)
    assert(space.collision_persistence == 3L)
    assert(space.enable_contact_graph == 0)

    # tests readonly attributes
    with pytest.raises(AttributeError):
        space.static_body = None


def test_space_gravity():
    space = cy.Space()
    assert(space.gravity.x == 0.)
    assert(space.gravity.y == 0.)
    space.gravity = (5, 10)
    assert(space.gravity.x == 5)
    assert(space.gravity.y == 10)
    space.gravity = cy.Vec2d(25, 50)
    assert(space.gravity.x == 25)
    assert(space.gravity.y == 50)

