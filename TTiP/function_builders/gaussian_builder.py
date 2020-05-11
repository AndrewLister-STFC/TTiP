r"""
The Gaussian function creates a symmetric function with a peak equal to the
`scale` at the location defined by `mean`.
As the distance from this peak increases, the function decays exponentially.
This decay is controlled by `sd`.

Args:
    - mean (numerical): The mean for the function.
    - sd (numerical): The standard deviation of the function.
    - scale (numerical): The amount to scale the function by.

The exact formula is:

.. math::

    \text{gaussian}(x, \text{mean}, \text{sd}, \text{scale}) =
        \text{scale}\times
        e^{-\frac{1}{2}\left(\frac{x-\text{mean}}{\text{sd}}\right)
        \cdot\left(\frac{x-\text{mean}}{\text{sd}}\right)}

Where:

- mean is a vector (comma seperated list) of length dim(x),
  or a scalar value that will be broadcast to a vector.
- sd is a vector (comma seperated list) of length dim(x),
  or a scalar value that will be broadcast to a vector.
- scale is a scalar value
"""
from firedrake import Function, SpatialCoordinate, exp

from TTiP.function_builders.function_builder import FunctionBuilder


class GaussianBuilder(FunctionBuilder):
    """
    A FunctionBuilder to create a gaussian function.

    Required Properties:
        mean (list<int or float>, int, float):
            This is the mean value for the gaussian (position of the peak).
            This should be either a list of the values, one for each direction,
            or a single value that will be used for every direction.
            e.g. In a 3D system:
                [2.1, 3.0, 2] Would be valid and represents [x, y, z]
                2.1 would be valid and is equivalent to [2.1, 2.1, 2.1]
        sd (list<int or float>, int, float):
            This is the standard deviation of the gaussian.
            As above, this can be a list or single value
        scale (int, float):
            This is the overall height of the gaussian.
    """
    # pylint: disable=too-few-public-methods
    properties = {'mean': (list, int, float),
                  'sd': (list, int, float),
                  'scale': (int, float)}

    def build(self):
        """
        Build the gaussian function.

        Raises:
            AttributeError: If required properties are not defined.

        Returns:
            Function: firedrake Constant set to the given value.
        """
        for k in self.properties:
            if self._props[k] is None:
                raise AttributeError('"{}" has not been defined.'.format(k))

        mean = self._props['mean']
        sd = self._props['sd']
        scale = self._props['scale']

        xs = SpatialCoordinate(self.mesh)
        if not isinstance(mean, list):
            mean = [mean] * len(xs)
        if not isinstance(sd, list):
            sd = [sd] * len(xs)

        gaussian = Function(self.V)
        components = [exp(-(x - m)**2 / 2 / s**2)
                      for x, m, s in zip(xs, mean, sd)]
        product = components[0]
        for c in components[1:]:
            product *= c

        gaussian.interpolate(scale * product)

        return gaussian
