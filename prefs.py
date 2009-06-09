#
# This file stores the global PythonCAD preferences, and
# is written itself in Python. Copy this file to the file
# '/etc/pythoncad/prefs.py' and it will be loaded and used
# to store global preferences for the program. Whenever
# a new image is opened, that image will use the global
# preferences for setting itself up. Each drawing window
# can then adjust these preferences by using the Preferences
# menus.
#
# When PythonCAD starts, a set of default values for the
# various options any image may set is stored, then the
# '/etc/pythoncad/prefs.py' file is searched for. If it
# is found, the values in the file will override the initial
# set of defaults. Variables defined in this file can
# therefore be commented out without problem.
#
# When defining a string value, the string can be in
# any case: 'UPPER', 'lower', or 'MiXeD'. The program will
# convert the string to upper case when testing the values
# entered here. Any time a string is given but the program
# fails to accept it due to case issues is a bug ...
#
# User Prefs
#
# This variable is meant as an adminstrators tool of
# disabling the reading of a preference file in the
# user's home directory. By default PythonCAD will look
# for a file in ${HOME}/.pythoncad/prefs.py after reading
# the global preference file '/etc/pythoncad/prefs.py'.
# If the user_prefs variable is set to False, the search
# for a user's preference file is not done.
#
# The prescence of this variable only makes sense in
# the '/etc/pythoncad.prefs' file.
#
# Valid choices: True, False

user_prefs = True

#
# Units
#
# The basic unit of length in an image.
#
# Valid choices:
# 'millimeters', 'micrometers', 'meters', 'kilometers',
# 'inches', 'feet', 'yards', 'miles'
#

units = 'millimeters'

#
# Chamfer Length
#
# The default chamfer length in an image.
#
# Valid values: Any numerical value 0.0 or greater
#

chamfer_length = 1.5

#
# Fillet Radius
#
# The default fillet radius in an image.
#
# Valid values: Any numerical value 0.0 or greater
#

fillet_radius = 2.0

#
# Leader arrow size
#
# This option sets the default arrow size on leader lines.
#
# Valid values: Any numerical value 0.0 or greater
#

leader_arrow_size = 10.0

#
# Highlight Points
#
# This option will activate the drawing of small boxes around
# the Point entities in an image.
#
# Valid choices: True, False
#

highlight_points = True

#
# Linetypes
#
# There are several default Linetypes provided in PythonCAD.
# If you want to define more, they are added here.
#
# Each Linetype is defined as a tuple of two objects:
#
# (name, dashlist)
#
# The name is a string or unicode string, and the dash list
# is either 'None' (meaning a solid line), or a list with
# an even number of integer values. Each value pair represents
# the on-off bit pattern in the line.
#
# Examples:
# A dashed linetype called 'dash' with 4 bits on then 4 bits off:
# (u'dash', [4, 4])
#
# A dashed linetype called 'dash2' with 10 bits on, 2 off, 6 on, 2 off
# (u'dash2', [10, 2, 6, 2]) # the "u" means unicode ...
#
# Add any new linetypes you wish in the linetypes list variable
#

linetypes = [
    # (u'dash', [4, 4]), # dash example above
    # (u'dash2', [10, 2, 6, 2]), # dash2 example above
    ]

#
# Colors
#
# By default PythonCAD starts with eight basic colors defined.
# If you want to add more, here is where to add them.
#
# A Color is defined in one of two ways:
#
# '#xxxxxx' - a hexidecimal string like '#ff00ff'
# (r, g, b) - a tuple with three integers giving the red, green, and
#             blue values. Each value must be 0 <= val <= 255.
#
# Add any new colors you wish to use in the colors list variable

colors = [
    # '#ffffff', # hexidecimal example
    # '#33cc77', # another hex example
    # (100, 50, 30), # tuple example
    # (255, 30, 180), # another tuple example
    ]

#
# Styles
#
# Styles define a common set of properties for objects like
# segments, circles, and arcs. There are eight default styles
# in PythonCAD, and adding more styles can be done here.
#
# Defining a style is done by creating a dictionary containing
# four keys:
#
# 'name' : Style name - A string
# 'linetype' : Style linetype - see the definition above
# 'color' : Style color - see the definition above
# 'thickness' : Style thickness - a positive float value.
#
# Older versions of PythonCAD expected the Style defintion
# to be in a tuple like the following:
#
# (name, linetype, color, thickness)
#
# This format is deprecated but still accepted.
#
# Examples:
#
# {'name' : u'style1',
#  'linetype' : (u'lt1', [10, 4]),
#  'color' : '#ffcc99',
#  'thickness' : 0.1
# }
# A style called 'style1', composed of a linetype called 'lt1'
# which is a dashed line 10 bits on, 4 off, drawn with the
# color '#ffcc99' and 0.1 units thick.
#
# Add any new styles you want to use to the 'styles' list
# variable below. Several examples are included to provide
# a starting guide for creating new styles.
#

styles = [
    # {'name' : u'style1',
    #  'linetype' : (u'lt1', [10, 4]),
    #  'color' : '#ffcc99',
    #  'thickness' : 0.1
    # },
    # {'name' : u'style2',
    #  'linetype' : (u'lt2', [6, 2, 10, 4]),
    #  'color' : '#cc00ff',
    #  'thickness' : 0.3
    # },
    # {'name' : u'style3',
    #  'linetype' : (u'lt3', [2, 6, 2, 2]),
    #  'color' : '#88ffbb',
    #  'thickness' : 0.2
    # }
    ]

#
# Default style
#
# Set this variable to the name of the Style you want the
# initial drawing style to be in PythonCAD. If you set this
# variable to None, or comment it out, the default Style
# defined within the program will be used.

default_style = None

#
# Style overrides
#
# In addition to setting the Style, some default entity properties
# can be set in this file. In setting one of the following values, the
# value defined in the default Style will be overriden.
#
# The examples below are all commented out. The values defined are
# arbitrary and for example purposes. Change the values as necessary
# and uncomment the variables you want to override the default Style
# values.
#
# line_type = (u'example', [5, 5, 8, 8])
# line_color = '#885533'
# line_thickness = 0.2
# 
#
# Dimension Styles
#
# A dimension style is a set of parameters that define
# how the dimension looks. Any dimension has a large number
# of attributes that can be set, so a dimension style is
# a way of grouping together these attributes into a common
# set and offering a means of making the dimensions look
# uniform.
#
# Defining a dimension style requires creating a dictionary
# with a certain keys and values. PythonCAD defines a single
# default dimension style, and any new dimension styles that
# are created here use that default style as a base, and the
# values in the new style then override the defaults.
#
# The list of dictionary keys and acceptable values is
# somewhat long. This list is given below with each key
# and the acceptable values for each key listed.
#
# Key: 'DIM_PRIMARY_FONT_FAMILY'
# Value: A string giving the font name
# Default: 'Sans'
#
# Key: 'DIM_PRIMARY_TEXT_SIZE'
# Value: A positive float value
# Default: 1.0
#
# Key: 'DIM_PRIMARY_FONT_WEIGHT'
# Value: One of 'normal', 'light', 'bold', or 'heavy'
# Default: 'normal'
#
# Key: 'DIM_PRIMARY_FONT_STYLE'
# Value: One of 'normal', 'oblique', or 'italic'
# Default: 'normal'
#
# Key: 'DIM_PRIMARY_FONT_COLOR'
# Value: A Color definition (see above), like (255, 255, 255) or '#ffffff'
# Default: '#ffffff'
#
# Key: 'DIM_PRIMARY_TEXT_ANGLE'
# Value: A float value
# Default: 0.0
#
# Key: 'DIM_PRIMARY_TEXT_ALIGNMENT'
# Value: One of 'left', 'center', or 'right'
# Default: 'center'
#
# Key: 'DIM_PRIMARY_PREFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'DIM_PRIMARY_SUFFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'DIM_PRIMARY_PRECISION'
# Value: An integer value where 0 <= value <= 15
# Default: 3
#
# Key: 'DIM_PRIMARY_UNITS'
# Value: One of 'millimeters', 'micrometers', 'meters', 'kilometers',
#        'inches', 'feet', 'yards', 'miles'
# Default: 'Millimeters'
#
# Key: 'DIM_PRIMARY_LEADING_ZERO'
# Value: True or False
# Default: True
#
# Key: 'DIM_PRIMARY_TRAILING_DECIMAL'
# Value: True or False
# Default: True
#
# Key: 'DIM_SECONDARY_FONT_FAMILY'
# Value: A string giving the font name
# Default: 'Sans'
#
# Key: 'DIM_SECONDARY_TEXT_SIZE'
# Value: A positive float value
# Default: 1.0
#
# Key: 'DIM_SECONDARY_FONT_WEIGHT'
# Value: One of 'normal', 'light', 'bold', or 'heavy'
# Default: 'normal'
#
# Key: 'DIM_SECONDARY_FONT_STYLE'
# Value: One of 'normal', 'oblique', or 'italic'
# Default: 'normal'
#
# Key: 'DIM_SECONDARY_FONT_COLOR'
# Value: A Color definition (see above), like (255, 255, 255) or '#ffffff'
# Default: '#ffffff'
#
# Key: 'DIM_SECONDARY_TEXT_ANGLE'
# Value: A float value
# Default: 0.0
#
# Key: 'DIM_SECONDARY_TEXT_ALIGNMENT'
# Value: One of 'left', 'center', or 'right'
# Default: 'center'
#
# Key: 'DIM_SECONDARY_PREFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'DIM_SECONDARY_SUFFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'DIM_SECONDARY_PRECISION'
# Value: An integer value where 0 <= value <= 15
# Default: u''
#
# Key: 'DIM_SECONDARY_UNITS'
# Value: One of 'millimeters', 'micrometers', 'meters', 'kilometers',
#        'inches', 'feet', 'yards', 'miles'
# Default: 'millimeters'
#
# Key: 'DIM_SECONDARY_LEADING_ZERO'
# Value: True or False
# Default: True
#
# Key: 'DIM_SECONDARY_TRAILING_DECIMAL'
# Value: True or False
# Default: True
#
# Key: 'DIM_OFFSET'
# Value: A float value of 0.0 or greater.
# Default: 1.0
#
# Key: 'DIM_EXTENSION'
# Value: A float value of 0.0 or greater.
# Default: 1.0
#
# Key: 'DIM_COLOR'
# Value: A Color definition (see above), like (255, 255, 255) or '#ffffff'
# Default: (255, 165, 0)
#
# Key: 'DIM_THICKNESS'
# Value: A float value of 0.0 or greater.
# Default: 0.0
#
# Key: 'DIM_POSITION'
# Value: One of 'split', 'above', or 'below'
# Default: 'split'
#
# Key: 'DIM_POSITION_OFFSET'
# Value: A float value
# Default: 0.0
#
# Key: 'DIM_ENDPOINT'
# Value: One of 'none', 'arrow', 'filled_arrow', 'slash', or 'circle'
# Default: None
#
# Key: 'DIM_ENDPOINT_SIZE'
# Value: A float vale of 0.0 or greater.
# Default: 1.0
#
# Key: 'DIM_DUAL_MODE'
# Value: True or False
# Default: False
#
# Key: 'DIM_DUAL_MODE_OFFSET'
# Value: A float value
# Default: 0.0
#
# Key: 'RADIAL_DIM_PRIMARY_PREFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'RADIAL_DIM_PRIMARY_SUFFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'RADIAL_DIM_SECONDARY_PREFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'RADIAL_DIM_SECONDARY_SUFFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'RADIAL_DIM_DIA_MODE'
# Value: True or False
# Default: False
#
# Key: 'ANGULAR_DIM_PRIMARY_PREFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'ANGULAR_DIM_PRIMARY_SUFFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'ANGULAR_DIM_SECONDARY_PREFIX'
# Value: A string or unicode string
# Default: u''
#
# Key: 'ANGULAR_DIM_SECONDARY_SUFFIX'
# Value: A string or unicode string
# Default: u''
#
#
# The keys that begin 'DIM_PRIMARY_' apply are specific to the
# primary dimension in any dimension, and 'DIM_SECONDARY_' are
# specific to the secondary dimension. 'RADIAL_DIM_' and
# 'ANGULAR_DIM_' are obviously applicible to those specific
# dimension types.
#
# 'DIM_OFFSET' is the distance between the dimensioned point and
# the start of the dimension bar, and 'DIM_EXTENSION' is the
# distance between where the dimension crossbar intersects the
# dimension bar and the end of the dimension bar. 'DIM_POSITION'
# will be used in placing the dimension text around the dimension
# crossbar. The names of the keys were chosen to be somewhat
# self explanatory, but they could change in future releases.
#
# Keys 'DIM_POSITION_OFFSET' and 'DIM_DUAL_MODE_OFFSET' act
# as placeholders for future refinement of dimension styles
# in positioning the dimension text.
#
# As a dimension style is built by overriding the default values,
# creating a new style only requires changing the fields that
# you wish to update. In the example below, the four fields
# 'dim_offset', 'dim_endpoint', 'dim_endpoint_size', and
# 'dim_extension' are modified.

example_dict = {
    'dim_offset' : 5.0,
    'dim_endpoint' : 'filled_arrow',
    'dim_endpoint_size' : 10.0,
    'dim_extension' : 5.0,
    }
#
# here is an example of a dimension style with more changes
#

dimstyle_example_2 = {
    'dim_primary_font_family' : 'Times',
    'dim_primary_text_size' : 24.0,
    'dim_primary_font_color' : '#dd44bb',
    'dim_primary_suffix' : u' mm',
    'dim_primary_precision' : 2,
    'dim_secondary_font_family' : 'Helvetica',
    'dim_secondary_text_size' : 18.0,
    'dim_secondary_font_color' : '#33ee55',
    'dim_secondary_suffix' : u' in.',
    'dim_secondary_units' : 'inches',
    'dim_offset' : 10.0,
    'dim_endpoint' : 'slash',
    'dim_endpoint_size' : 10.0,
    'dim_extension' : 5.0,
    'radial_dim_primary_prefix' : u'R. ',
    'radial_dim_primary_suffix' : u' mm',
    'radial_dim_secondary_prefix' : u'R. ',
    'radial_dim_secondary_suffix' : u' in.',
    'dim_dual_mode' : True,
    }
#
# The creation of the dimension style is done with by creating
# a tuple containing two objects:
#
# (name, dict)
#
# name: The dimension style name
# dict: The dictionary containing the values for the dimension style
#
# Add any dimension styles you create to the dimstyles list below.

dimstyles = [
    # (u'example_dimstyle', example_dict), # example
    # (u'ex2' , dimstyle_example_2), # another example
    ]
#
# Default dimension style
#
# Set this variable to the name of the dimension style you
# want PythonCAD to use by default. If you define this variable
# to None, or comment it out, the default dimension style
# is used.

default_dimstyle = None

#
# Each of the DimStyle keys can also be used to specify
# an overriding value for the attribute defined in the
# DimStyle. The keys are listed below with possible values
# defined for example purposes. Change the values and
# uncomment the lines as desired.

# dim_primary_font_family = 'Sans'
# dim_primary_text_size = 12.0
# dim_primary_font_weight = 'bold'
# dim_primary_font_style = 'italic'
# dim_primary_font_color = '#ffffaa'
# dim_primary_text_angle = 0.0
# dim_primary_text_alignment = 'left'
# dim_primary_prefix = u'Dim: '
# dim_primary_suffix = u' [Dim]'
# dim_primary_precision = 5
# dim_primary_units = 'inches'
# dim_primary_leading_zero = False
# dim_primary_trailing_decimal = False
# dim_secondary_font_family = 'Times'
# dim_secondary_text_size = 10.0
# dim_secondary_font_weight = 'heavy'
# dim_secondary_font_style = 'oblique'
# dim_secondary_font_color = '#00ccaa'
# dim_secondary_text_angle = 0.0
# dim_secondary_text_alignment = 'left'
# dim_secondary_prefix = u'Dim: '
# dim_secondary_suffix = u' [Dim]'
# dim_secondary_precision = 4
# dim_secondary_units = 'inches'
# dim_secondary_leading_zero = False
# dim_secondary_trailing_decimal = False
# dim_offset = 5.0
# dim_extension = 10.0
# dim_color = '#55aacc'
# dim_thickness = 1.5
# dim_position = 'above'
# dim_position_offset = 1.0
# dim_endpoint = 'slash'
# dim_endpoint_size = 5.0
# dim_dual_mode = True
# dim_dual_mode_offset = 1.0
# radial_dim_primary_prefix = u'R. '
# radial_dim_primary_suffix = u' [R]'
# radial_dim_secondary_prefix = u'R. '
# radial_dim_secondary_suffix = u' [R]'
# radial_dim_dia_mode = True
# angular_dim_primary_prefix = u'Deg: '
# angular_dim_primary_suffix = u' [Deg]'
# angular_dim_secondary_prefix = u'Deg: '
# angular_dim_secondary_suffix = u' [Deg]'
#

# Text styles
#
# A text style defines a common set of text attributes
# that are used to define visual elements of some text.
# A single text style is defined in PythonCAD, so if you
# want more text styles here is where to add them.
#
# Defining a text style is done by creating a dictionary
# with the following keys:
#
# 'name': TextStyle name
# 'family': Font family, like 'Sans', 'Times', etc.
# 'weight': Font weight - 'normal', 'light', 'bold', or 'heavy'
# 'style': Font style - 'normal', 'italic', or 'oblique'
# 'size': Text size - a float value greater than 0.
# 'color': The TextStyle color - 
# 'angle': The angle at which the text is displayed - a float value
# 'alignment': Text alignment - 'left', 'center', or 'right'
#
# The keys can be specified in any order, but all must be provided.
# Extra keys are ignored.
#
# Earlier versions of PythonCAD accepted a tuple-based TextStyle
# definition as seen below:
#
# (name, family, size, style, weight, color)
#
# This format is still accepted but is deprecated. Tuple-based
# TextStyle definitions lacked the 'angle' and 'alignment' fields,
# so when encountered the definition will default to the 'angle'
# being 0.0 and 'alignment' being 'left.
# 
# The two examples below define a one TextStyle named 'default'
# and a second TextStyle named 'fancy':
#
# {'name' : 'default',
#  'family' : 'sans',
#  'size' : 10.0,
#  'style' : 'normal',
#  'weight' : 'normal',
#  'color' : '#ff00cc',
#  'angle' : 0.0,
#  'alignment' : 'left'
#  }
#
# {'name' : 'fancy',
#  'family' : 'helvetica',
#  'size' : 20.0,
#  'style' : 'italic',
#  'weight' : 'bold',
#  'color' : '#ffff00',
#  'angle' : 0.0,
#  'alignment' : 'center'
#
#
# Add more text styles you wish to use within the 'textstyles' list.
#

textstyles = []

#
# Default text style
#
# Set this variable to the name of the TextStyle you want
# PythonCAD to use by default. If you define this variable
# to None, or comment it out, the default TextStyle defined
# within the program is used
#

default_textstyle = None

#
# Text properties
#
# In addition to setting the text styles, some default font properties
# can be set in this file. In setting one of the following values, the
# value defined in the default TextStyle will be overriden.
#
# The examples below are all commented out. The values defined are
# arbitrary and for example purposes. Change the values as necessary
# and uncomment the variables you want to override the default TextStyle
# values.
#
# font_family = 'Sans'
# text_size = 18.0
# font_weight = 'light'
# font_style = 'italic'
# font_color = '#ff00ff'
# text_angle = 0.0
# text_alignment = 'center'
#
# Miscellaneous options
#
# Autosplitting
#
# This option will activate the automatic splitting of segments,
# circles, and arcs if a new point is added directly on the object.
#
# Valid choices: True, False
#

autosplit = True
