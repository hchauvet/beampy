#!/usr/bin/env python3

"""
Usefull function to deal with modules
"""
import re


def get_maximum_layer(modules: list) -> int:
    """Return the maximum of layers of a beampy modules list.
    Each beampy module has a layer list (stored in layers attribute).
    The layers list could contains:
    - a number (the layer)
    - a string (like range(0,max,1))
    Parameters:
    -----------

    modules, list:
        List of beampy_module on which to compute the maximum layer set.
    """

    maxlayer = 0
    for mod in modules:

        # When the range of layer is defined as a string (usual
        # with an unknown maximum), take the start value as
        # maximum layer
        if isinstance(mod.layers, str):
            if mod.layers.startswith('range'):
                start = re.findall('[0-9]+', mod.layers)[0]
                tmpmax = int(start)
            else:
                tmpmax = 0 # case of "max"
        else:
            tmpmax = max(mod.layers)

        if tmpmax > maxlayer:
            maxlayer = tmpmax

    return maxlayer


def get_minimum_layer(modules: list) -> int:
    """Return the minimum layer of a list of modules
    """

    minlayer = 0
    for mod in modules:

        # When the range of layer is defined as a string (usual
        # with an unknown maximum), take the start value as
        # maximum layer
        if isinstance(mod.layers, str):
            if mod.layers.startswith('range'):
                start = re.findall('[0-9]+', mod.layers)[0]
                tmpmin = int(start)
            else:
                tmpmin = 100000 # case of "max" set a dummy high value
        else:
            tmpmin = min(mod.layers)

        if tmpmin < minlayer:
            minlayer = tmpmin

    return minlayer


def stringlayers_to_int(layers: list, maxlayer: int):
    """Convert string layer:
    - "range(0, max, 1)" -> range(0, maxlayer, 1)
    - "max" -> maxlayer
    """

    if layers.startswith('range'):
        lmax = maxlayer + 1
        parsed_range_int = re.findall('[0-9]+', layers)
        start = int(parsed_range_int[0])
        step = int(parsed_range_int[-1])
        intlayers = list(range(start, lmax, step))
    elif 'max' in layers:
        intlayers = [maxlayer]
    else:
        raise ValueError("Unkown layer string format got %s" % layers)

    return intlayers


def unique_layers(modules: list, maxlayer: int, check_consistancy=True) -> list:
    """Get the list of unique layer number in a given
    set of beampy modules.
    """

    all_layers = []
    for mod in modules:
        # Convert string layers if needed
        if isinstance(mod.layers, str):
            converted_layers = stringlayers_to_int(mod.layers, maxlayer)
            mod.add_layers(converted_layers)
        else:
            mod.add_layers(mod.layers)

        all_layers += mod.layers

    # Make layers unique (using python set property) and sorted
    u_layers = sorted(set(all_layers))

    # Chaque layer consistancy
    if check_consistancy and u_layers != list(range(0, maxlayer+1, 1)):
        raise ValueError('Layers are not consecutive. I got %s, I should have %s' % (str(u_layers),
                                                                                     str(list(range(0, maxlayer+1)))))

    return u_layers
