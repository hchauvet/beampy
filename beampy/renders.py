# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:27:48 2015

@author: hugo
"""

from beampy.document import document
from beampy.functions import *
import time
from beampy.terminal_output import * #To display beampy messages correctly

def render_slide( slide ):
    """
        Function to render a slide to an svg figure
    """

    pre = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    """

    print( '-'*20 + ' slide_%i '%slide['num'] + '-'*20 )
    if slide['style'] == None:
        slide['style'] = ''

    out = pre+"""\n<svg width='%ipx' height='%ipx' style='%s'
    xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:cc="http://creativecommons.org/ns#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    >"""%(document._width, document._height, slide['style'])

    animout = [] #dict to store animations
    cpt_anim = slide['cpt_anim'] #animations counter
    element_id = 0 #counter for element
    scriptout = slide['scriptout'] #String to store javascript output
    htmlout = slide['htmlout'] #for html
    ytop = 0 #Offset of the title

    #Check if their is a title in the slide
    if slide['title'] != None:
        #Check if we have a title on slide
        ytop = float(convert_unit(slide['title']['args']['reserved_y']))

    #Check if elements can be obtained from cache or render the element
    cptcache = 0
    t = time.time()
    for i, ct in slide['contents'].iteritems():
        cptcache = render_content( ct, cptcache )
        #print ct.keys()

    if cptcache > 0:
        if cptcache == 1:
            outstr = 'Get %i element from cache'%(cptcache)
        else:
            outstr = 'Get %i elements from cache'%(cptcache)

        print(outstr)

    print('Rendering elements in %0.3f sec'%(time.time()-t))
    t = time.time()

    #Render contents and place groups
    htmlingroup = []
    all_height = {}

    for cpt, i in enumerate(slide['element_keys']):
        ct = slide['contents'][i]
        #Si on trouve des texts
        if 'type' in ct and ct['render'] != None:
            #print(ct['type'])
            #Check if it's a group
            if ct['type'] == 'group':
                #render the group
                tmpsvg = ct['render']( ct )
                ct['rendered'] = tmpsvg

            #get htmlcontents position
            if ct['type'] == 'html' and 'group_id' in ct:
                htmlingroup += [i]
            else:
                #Check if it's an auto placement or we can place the element
                if ct['positionner'].y['align'] == 'auto':
                    all_height[cpt] = {"height": ct['positionner'].height, "id":i}
                else:
                    ct['positionner'].place( (document._width, document._height), ytop=ytop )



    #Manage auto placement
    if all_height != {}:
        auto_place_elements(all_height, (document._width, document._height),
                            'y', slide['contents'], ytop)

    #Extra operations for html contents
    if htmlingroup != []:

        for i in htmlingroup:
            ct = slide['contents'][i]
            #add off set to the html div position
            igroup = slide['element_keys'].index(ct['group_id'])
            ct['positionner'].x['final'] += slide['contents'][ct['group_id']]['positionner'].x['final']
            ct['positionner'].y['final'] += slide['contents'][ct['group_id']]['positionner'].y['final']

    #Write rendered content
    for key in slide['element_keys']:
        ct = slide['contents'][key]
        if 'rendered' in ct:
            #add the content to the output
            out, animout, htmlout, cpt_anim = write_content(ct, out, animout, htmlout, cpt_anim)
            #Check if we have javascript to output
            if 'script' in ct['args']:
                scriptout += ct['args']['script']

    #Add grid and fancy stuff...
    if document._guide:
        available_height = document._height - ytop
        out += '<g><line x1="400" y1="0" x2="400" y2="600" style="stroke: #777"/></g>'
        out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>'%(ytop + available_height/2.0, ytop + available_height/2.0)
        out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>'%(ytop, ytop)

    #Close the main svg
    out += "\n</svg>\n"

    slide['svg_output'] = out
    if animout != []:
        slide['svg_animations'] = animout

    #Add html
    if htmlout != "":
        slide['html_output'] = htmlout
        #print htmlout

    #Add script to the end of svg_output
    if scriptout != "":
        slide['script'] = scriptout

    print('Placing elements in %0.3f'%(time.time()-t))

    return out


def compute_equal_space(available_size, all_elements_size, offset=0):
    """
        Function to return an equal space between elements
    """

    available_size -= offset
    total_content_size = sum(all_elements_size)

    dspace = (available_size - total_content_size)/float( len(all_elements_size) + 1 )

    return dspace

def auto_place_elements(all_size, container_size, axis, contents, ytop):
    """
        container_size = (document._width, document._height)
    """
    if axis == 'x':
        max_size = container_size[0]
    if axis == 'y':
        max_size = container_size[1]

    ds = compute_equal_space(max_size, [k['height'] for k in all_size.values()], ytop)
    cpts = ds + ytop

    for data in all_size.values():
        elem = data['id']
        height = data['height']
        if axis == 'y':
            contents[elem]['positionner'].y['shift'] = cpts
            contents[elem]['positionner'].y['align'] = 'top'
            contents[elem]['positionner'].y['unit'] = 'px'

        if axis == 'x':
            contents[elem]['positionner'].x['shift'] = cpts
            contents[elem]['positionner'].x['align'] = 'left'
            contents[elem]['positionner'].x['unit'] = 'px'

        contents[elem]['positionner'].place( container_size, ytop=ytop )
        cpts += ds + height

def render_content( slide_content, cptcache ):
    """
        Run render of the given content or check if it's cached
    """
    slide = document._contents[gcs()]
    ct = slide_content
    if document._cache != None:
        ct_cache = document._cache.is_cached('slide_%i'%slide['num'], ct)
        if ct_cache != None:
            tmpc = ct_cache
            ct['rendered'] = tmpc['rendered']
            ct['positionner'].update_size( tmpc['width'], tmpc['height'] )
            cptcache += 1
            #print ct.keys()
        elif 'render' in ct and ct['render'] != None:
            #print("element %i not cached"%ct['positionner'].id)
            tmpsvg = ct['render']( ct )
            ct['rendered'] = tmpsvg
            document._cache.add_to_cache('slide_%i'%slide['num'], ct )

    elif 'render' in ct and ct['render'] != None :
        tmpsvg = ct['render']( ct )
        ct['rendered'] = tmpsvg

    return cptcache

def write_content(ct, svgoutputlist, animationoutputlist, htmloutputlist, cpt_anim):
    """
        function to write rendered content ct in the good output list
        svgoutputlist -> svg
        animationoutputlist -> svganimation
        htmloutputlist -> htmlcontent
    """

    if ct['type'] in ['animatesvg'] and document._output_format=='html5':
        #Pre cache raster images
        frames_svg_cleaned, all_images = pre_cache_svg_image(ct['rendered'])
        #Add an animation to animout dict
        animationoutputlist += [{}]
        animationoutputlist[cpt_anim]['header'] = "%s"%(''.join(all_images))
        animationoutputlist[cpt_anim]['config'] = {'autoplay':ct['args']['autoplay'], 'fps': ct['args']['fps']}
        #animout['header'] += '<g id="maingroup" transform="translate(%s,%s)">'%(tmpx,tmpy)

        svgoutputlist += "<defs id='pre_loaded_images_%i'></defs>"%(cpt_anim)
        svgoutputlist += '<g id="svganimate_%i" transform="translate(%s,%s)" onclick="Beampy.animatesvg(%i,%i);"> </g>'%(cpt_anim, ct['positionner'].x['final'],ct['positionner'].y['final'], cpt_anim, ct['args']['fps'])

        animationoutputlist[cpt_anim]['frames'] = {}
        for i in xrange(len(frames_svg_cleaned)):
            animationoutputlist[cpt_anim]['frames']['frame_%i'%i] = frames_svg_cleaned[i]

        #Add +1 to anim counter
        cpt_anim += 1

    elif ct['type'] == 'html' and document._output_format=='html5':
        htmloutputlist += """<div style="position: absolute; left: %spx; top: %spx;"> %s </div>"""%(ct['positionner'].x['final'], ct['positionner'].y['final'], ct['rendered'])
        htmloutputlist += "</br>"
        #print htmloutputlist

    else:
        if ct['type'] not in ['html']:
            svgoutputlist += '<g transform="translate(%s,%s)">'%(ct['positionner'].x['final'], ct['positionner'].y['final'])
            svgoutputlist += ct['rendered']

            #add a box around groups
            if document._text_box and ct['type'] == 'group':
                svgoutputlist +="""<rect x="0"  y="0" width="%s" height="%s" style="stroke:#009900;stroke-width: 1;stroke-dasharray: 10 5;fill: none;" />"""%(ct['positionner'].width, ct['positionner'].height)

            svgoutputlist += '</g>'

    return svgoutputlist, animationoutputlist, htmloutputlist, cpt_anim
