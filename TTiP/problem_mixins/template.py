"""
Contains the <name> class for extending problems.
"""

class <name>:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow <function>.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(<name>, Problem):
           pass

    Attributes:
        <defined attributes>
    """
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for <name>.

        <description>
        """
        super().__init__(*args, **kwargs)
        <init>

    <other functions>
