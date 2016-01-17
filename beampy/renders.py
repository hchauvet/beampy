# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:27:48 2015

@author: hugo
"""

from beampy.document import document
from beampy.functions import *
import time

def render_slide( slide ):
    """
        Function to render a slide to an svg figure
    """

    pre = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    """
    print( '-'*10 + 'slide_%i'%slide['num'] + '-'*10 )
    if slide['style'] == None:
        slide['style'] = ''

    out = pre+"""\n<svg width='%ipx' height='%ipx' style='%s'
    xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:cc="http://creativecommons.org/ns#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    >"""%(document._width,document._height,slide['style'])

    #old style 'position: absolute; top:0px; left:0px;' but seems unused and cause inkscape complains when export to pdf

    animout = [] #dict to store animations
    cpt_anim = 0 #animations counter
    element_id = 0 #counter for element
    scriptout = "" #String to store javascript output
    htmlout = "" #for html
    ytop = 0 #Offset of the title

    #Render the content of the slide
    if slide['title'] != None:
        #Check cache
        #slide['title']['positionner'].id = 'title'
        if document._cache != None:
            ct_cache = document._cache.is_cached('slide_%i'%slide['num'], slide['title'])
            if ct_cache != None:
                tmpc = ct_cache
                slide['title']['rendered'] =  tmpc['rendered']
                slide['title']['positionner'].update_size( tmpc['width'], tmpc['height'] )
                print('render title from cache')
            else:
                print('render title')
                tmpsvg = slide['title']['render']( slide['title'] )
                slide['title']['rendered'] = tmpsvg
                document._cache.add_to_cache('slide_%i'%slide['num'], slide['title'])

        else:
            print('render title')
            #tmpsvg, tmpw, tmph = slide['title']['render']( slide['title']['content'], slide['title']['args'], slide['title']['args']['usetex'] )
            tmpsvg, _, _ = slide['title']['render']( slide['title'] )
            slide['title']['rendered'] = tmpsvg

        #place the title
        slide['title']['positionner'].place( (document._width, document._height) )

        #Convert arguments to svg arguments
        #out +=  '\n<g transform="translate(%s,%s)">\n'%( convert_unit(slide['title']['args']['x']), convert_unit(slide['title']['args']['y']))
        out +=  '\n<g transform="translate(%s,%s)">\n'%( slide['title']['positionner'].x['final'], slide['title']['positionner'].y['final'] )
        out += slide['title']['rendered']
        out += "\n</g>\n"

        #Check if we have a title on slide
        ytop = float(convert_unit(slide['title']['args']['reserved_y']))

    #Check if elements can be obtained from cache or render the element
    cptcache = 0
    t = time.time()
    for i, ct in enumerate(slide['contents']):
        if document._cache != None:
            ct_cache = document._cache.is_cached('slide_%i'%slide['num'], ct)
            if ct_cache != None:
                tmpc = ct_cache
                ct['rendered'] = tmpc['rendered']
                ct['positionner'].update_size( tmpc['width'], tmpc['height'] )
                cptcache += 1
                #print ct.keys()
            else:
                print("element %i not cached"%ct['positionner'].id)
                tmpsvg = ct['render']( ct )
                ct['rendered'] = tmpsvg
                document._cache.add_to_cache('slide_%i'%slide['num'], ct )

        else:
            tmpsvg = ct['render']( ct )
            ct['rendered'] = tmpsvg

        #print ct.keys()

    print('Rendering elements in %f sec'%(time.time()-t))


            #print ct.keys()

    if cptcache > 0:
        if cptcache == 1:
            outstr = '[Slide %i] Get %i element from cache'%(slide['num'], cptcache)
        else:
            outstr = '[Slide %i] Get %i elements from cache'%(slide['num'], cptcache)

        print(outstr)


    t = time.time()
    #Render the content of the slide
    #In two steps:
    #   1 -> transform to svg and get width and height of each element
    #   2 -> Place elements on page, vertical distribution and horizontal alignement
    all_height = {}
    groups = slide['groups']

    #2 cases is their groups in the current slides or not
    if len(groups)>0:
        for group in groups:
            group_contents = slide['contents'][group['content_start']:group['content_stop']]

            #If the group width and height are not defined
            #set group width and height to the sum of elements width and height
            if group['positionner'].width == None:
                group['positionner'].width = max( [ct['positionner'].width for ct in group_contents] )

            if group['positionner'].height == None:
                group['positionner'].height = sum( [ct['positionner'].height+ct['positionner'].y['shift'] for ct in group_contents] )

            for i, ct in enumerate(group_contents):
                if ct['positionner'].y['align'] == 'auto':
                    all_height[i] = ct['positionner'].height
                else:
                    ct['positionner'].place( (group['positionner'].width, group['positionner'].height) )

                #Check if we have javascript to output
                if 'script' in ct['args']:
                    scriptout += ct['args']['script']


            #Manage autoplacement
            if all_height != {}:
                auto_place_elements(all_height, (group['positionner'].width, group['positionner'].height),
                                    'y', group_contents, ytop=0)
                all_height = {} #reset all_height dict

            #Update group size to fit the min max of all elements
            #set_group_size(group, slide)
            #Create the correct svg for the group and then remove content from the slide['contents']['rendered']
            #Add a global content for the group
            groupcontent = {'type': 'group', 'args': group['args'],
                            'content': '',
                            'positionner': group['positionner'],
                            'render': render_group}

            #groupcontent['content'] = ''
            for i, ct in enumerate(group_contents):
                if 'rendered' in ct and ct['type'] not in ['html']:
                    #Add rendered content to groupcontent
                    groupcontent['content'], animout, htmlout, cpt_anim = write_content(ct, groupcontent['content'], animout, htmlout, cpt_anim)

                    #remove the rendered part from slides content and set render to None
                    slide['contents'][group['content_start']+i]['render'] = None #not processed in the next loop
                    slide['contents'][group['content_start']+i].pop('rendered')

            #Add content to group list
            group['content'] = groupcontent
            #print groupcontent

    #Reloop over group to add them to slide contents
    for group in groups:
        #Add groupcontent to the slide contents
        slide['contents'].insert(group['content_start'], group['content'])


    #Render contents and place groups
    htmlingroup = []
    for i, ct in enumerate(slide['contents']):
        #Si on trouve des texts
        if 'type' in ct and ct['render'] != None:
            #Check if it's a group
            if ct['type'] == 'group':
                #render the group
                tmpsvg, _, _ = ct['render']( ct )
                ct['rendered'] = tmpsvg

            #get htmlcontents position
            if ct['type'] == 'html' and 'group_id' in ct:
                htmlingroup += [i]
            else:
                #Check if it's an auto placement or we can place the element
                if ct['positionner'].y['align'] == 'auto':
                    all_height[i] = ct['positionner'].height
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
            ct['positionner'].x['final'] += groups[ct['group_id']-1]['positionner'].x['final']
            ct['positionner'].y['final'] += groups[ct['group_id']-1]['positionner'].y['final']

    #Write rendered content
    for ct in slide['contents']:
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

    print('Placing elements in %f'%(time.time()-t))

    return out


def compute_equal_space(available_size, all_elements_size, offset=0):
    """
        Function to return an equal space between elements
    """

    available_size -= offset
    total_content_size = sum([float(all_elements_size[a]) for a in all_elements_size])

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

    ds = compute_equal_space(max_size, all_size, ytop)
    cpts = ds + ytop
    for elem in all_size:
        if axis == 'y':
            contents[elem]['positionner'].y['shift'] = cpts
            contents[elem]['positionner'].y['align'] = 'top'
            contents[elem]['positionner'].y['unit'] = 'px'

        if axis == 'x':
            contents[elem]['positionner'].x['shift'] = cpts
            contents[elem]['positionner'].x['align'] = 'left'
            contents[elem]['positionner'].x['unit'] = 'px'

        contents[elem]['positionner'].place( container_size, ytop=ytop )
        cpts += ds + all_size[elem]

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

def render_group( ct ):
    """
        group render
    """

    if ct['args']["background"] != None:
        pre_rect = '<rect width="%s" height="%s" style="fill:%s;" />'%(ct['positionner'].width, ct['positionner'].height, ct['args']['background'])
    else:
        pre_rect = ''

    return pre_rect + ct['content'], ct['positionner'].width, ct['positionner'].height

def set_group_size(group, slide):
    group_contents = slide['contents'][group['content_start']:group['content_stop']]

    xgroup = [ ct['positionner'].x['final'] for ct in group_contents ]
    ygroup = [ ct['positionner'].y['final'] for ct in group_contents ]

    xmin = min( xgroup )
    xmax = max( [ ct['positionner'].x['final']+ct['positionner'].width for ct in group_contents ] )
    ymin = min( ygroup )
    ymax = max( ygroup )
    ymax += group_contents[ygroup.index(ymax)]['positionner'].height

    #print xmax, xmin, ymax, ymin
    width = xmax - xmin
    height = ymax - ymin

    #update group size
    group['positionner'].update_size( width, height )
