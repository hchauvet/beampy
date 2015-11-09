# -*- coding: utf-8 -*-
"""
Created on Fri May 15 16:27:48 2015

@author: hugo
"""

from beampy.document import document
from beampy.functions import *
#import os
#import glob
#from bs4 import BeautifulSoup
#import re
#from PIL import Image

def render_slide( slide ):
    """
        Function to render a slide to an 800x600 svg figure
    """

    pre = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    """

    if slide['style'] == None:
        slide['style'] = ''

    out = pre+"""\n<svg width='%ipx' height='%ipx' style='position: absolute; top:0px; left:0px; %s' xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n"""%(document._width,document._height,slide['style'])
    animout = [] #dict to store animations
    cpt_anim = 0 #animations counter
    element_id = 0 #counter for element
    scriptout = "" #String to store javascript output
    htmlout = "" #for html

    #Render the content of the slide
    if slide['title'] != None:
        #Convert arguments to svg arguments
        out +=  '\n<g transform="translate(%s,%s)">\n'%( convert_unit(slide['title']['args']['x']), convert_unit(slide['title']['args']['y']))
        tmpsvg, tmpw, tmph = slide['title']['render']( slide['title']['content'], slide['title']['args'], slide['title']['args']['usetex'] )
        out += tmpsvg
        #out += "\n</svg>"
        out += "\n</g>\n"
        #out += '<g><line x1="%s" y1="%s" x2="10cm" y2="%s" style="stroke: #000000"/></g>'%(convert_unit("1cm"),convert_unit(slide['title']['args']['y']),convert_unit(slide['title']['args']['y']))

    #Check if elements can be obtained from cache
    cptcache = 0
    for i, ct in enumerate(slide['contents']):

        if document._cache != None:
            ct['id'] = i
            ct_cache = document._cache.is_cached('slide_%i'%slide['num'], ct)
            if ct_cache != None:
                slide['contents'][i] = ct_cache
                cptcache += 1

            #print ct.keys()

    if cptcache > 0:
        if cptcache == 1:
            outstr = '[Slide %i] Get %i element from cache'%(slide['num'], cptcache)
        else:
            outstr = '[Slide %i] Get %i elements from cache'%(slide['num'], cptcache)

        print(outstr)


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
            group_contents_all_height = {}
            group_height = 0
            tmp_width = []
            for i, ct in enumerate(group_contents):

                if 'type' in ct and ct['render'] != None:
                    ct['id'] = i + group['content_start']

                    #Check if the element is already in cache
                    if ('renderedgroup' in ct) or ('rendered' in ct):
                        if ct['type'] in 'html':
                            tmph, tmpw = ct['renderedgroup']['height'], ct['renderedgroup']['width']
                        else:
                            tmph, tmpw = ct['rendered']['height'], ct['rendered']['width']

                        #print('elem %i from cache'%i)
                    else:
                        #print('elem %i rendered'%i)
                        #Check if we need to render html outside of svg
                        if ct['type'] == 'html':
                            tmphtml, tmpw, tmph = ct['render']( ct['content'], ct['args'] )
                            ct['renderedgroup'] = {"group_id":group['args']['group_id'],"width":tmpw,"height":tmph}
                            #print("Warning html type (video and bokeh) are not placed in groups")
                        else:
                            tmpsvg, tmpw, tmph = ct['render']( ct['content'], ct['args'] )
                            ct['rendered'] = {"svg":tmpsvg,"width":tmpw,"height":tmph, "group_id":group['args']['group_id']}

                    #print tmpw, tmph
                    #Add content to the cache
                    if document._cache != None:
                        document._cache.add_to_cache('slide_%i'%slide['num'], ct)


                    group_height += tmph
                    tmp_width += [tmpw]
                    #Test if we have a relative offset of the
                    if i != 0:
                        if '+' in ct['args']['y'][0]:
                            group_height += float(convert_unit(ct['args']['y'][1:]))

                        if '+' in ct['args']['x'][0]:
                            tmp_width[-1] += float(convert_unit(ct['args']['x'][1:]))

                    if ct['args']['y'] == 'auto':
                        group_contents_all_height[i] = tmph

            if group['args']['width'] == None:
                group['args']['width'] = max(tmp_width)
            if group['args']['height']  == None:
                group['args']['height'] = group_height


            #Place elements in the groups
            #print group['args']['height'], group['args']['width']
            place_content(group_contents, group['args']['height'], group['args']['width'],
                          xtop=0, all_height=group_contents_all_height)
            #Create the correct svg for the group and then remove content from the slide['contents']['rendered']

            #Add a global content for the group
            groupcontent = {'type': 'group', 'args': group['args'],
                            'content': '',
                            'render': render_group}

            #groupcontent['content'] = ''
            for i, ct in enumerate(group_contents):
                if 'rendered' in ct:
                    #Add rendered content to groupcontent
                    groupcontent['content'], animout, htmlout, cpt_anim = write_content(ct, groupcontent['content'], animout, htmlout, cpt_anim)

                    #remove the rendered part from slides content and set render to None
                    slide['contents'][group['content_start']+i]['render'] = None #not processed in the next loop
                    slide['contents'][group['content_start']+i].pop('rendered')

            #Add content to group list
            group['content'] = groupcontent
            #print groupcontent

        #Need a second loop to add groups to slide contents
        for group in groups:
            #Add groupcontent to the slide contents
            slide['contents'].insert(group['content_start'], group['content'])


    #Render contents and place groups
    for i, ct in enumerate(slide['contents']):
        #Si on trouve des texts
        if 'type' in ct and ct['render'] != None:
            ct['id'] = i

            #Check if the element is already in cache
            if 'rendered' in ct:
                tmph, tmpw = ct['rendered']['height'], ct['rendered']['width']
                #print(ct['type'])
            else:

                #Check if we need to render html outside of svg
                if ct['type'] == 'html':
                    tmphtml, tmpw, tmph = ct['render']( ct['content'], ct['args'] )
                    ct['rendered'] = {"html":tmphtml,"width":tmpw,"height":tmph}
                else:
                    #Use the defined render function in the content dict['render']
                    tmpsvg, tmpw, tmph = ct['render']( ct['content'], ct['args'] )
                    ct['rendered'] = {"svg":tmpsvg,"width":tmpw,"height":tmph}

            #Add content to the cache
            if document._cache != None:
                document._cache.add_to_cache('slide_%i'%slide['num'], ct)

            if ct['args']['y'] == 'auto':
                all_height[i] = tmph



    #Place elements on page

    #Check if we have a title on slide
    if slide['title'] != None:
        xtop = float(convert_unit(slide['title']['args']['reserved_y']))
    else:
        xtop = 0

    place_content(slide['contents'], document._height, document._width, xtop, all_height)

    #add group to contents svg to place them
    for ct in slide['contents']:

        if 'rendered' in ct:
            #add the content to the output
            out, animout, htmlout, cpt_anim = write_content(ct, out, animout, htmlout, cpt_anim)
            #Check if we have javascript to output
            if 'script' in ct['args']:
                scriptout += ct['args']['script']

    #Add grid and fancy stuff...
    if document._guide:
        available_height = document._height - xtop
        out += '<g><line x1="400" y1="0" x2="400" y2="600" style="stroke: #777"/></g>'
        out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>'%(xtop + available_height/2.0, xtop + available_height/2.0)
        out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>'%(xtop, xtop)
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

    return out


def write_content(ct, svgoutputlist, animationoutputlist, htmloutputlist, cpt_anim):
    """
        function to write rendered content ct in the good output list
        svgoutputlist -> svg
        animationoutputlist -> svganimation
        htmloutputlist -> htmlcontent
    """

    if ct['type'] in ['animatesvg'] and document._output_format=='html5':
        #Pre cache raster images
        frames_svg_cleaned, all_images = pre_cache_svg_image(ct['rendered']['svg'])
        #Add an animation to animout dict
        animationoutputlist += [{}]
        animationoutputlist[cpt_anim]['header'] = "%s"%(''.join(all_images))
        animationoutputlist[cpt_anim]['config'] = {'autoplay':ct['args']['autoplay'], 'fps': ct['args']['fps']}
        #animout['header'] += '<g id="maingroup" transform="translate(%s,%s)">'%(tmpx,tmpy)

        svgoutputlist += "<defs id='pre_loaded_images_%i'></defs>"%(cpt_anim)
        svgoutputlist += '<g id="svganimate_%i" transform="translate(%s,%s)" onclick="Beampy.animatesvg(%i,%i);"> </g>'%(cpt_anim, ct['args']['x'],ct['args']['y'], cpt_anim, ct['args']['fps'])

        animationoutputlist[cpt_anim]['frames'] = {}
        for i in xrange(len(frames_svg_cleaned)):
            animationoutputlist[cpt_anim]['frames']['frame_%i'%i] = frames_svg_cleaned[i]

        #Add +1 to anim counter
        cpt_anim += 1

    elif ct['type'] == 'html' and document._output_format=='html5':
        htmloutputlist += """<div style="position: fixed; left: %spx; top: %spx;"> %s </div>"""%(ct['args']['x'],ct['args']['y'],ct['rendered']['html'])
        htmloutputlist += "</br>"
        #print htmloutputlist

    else:
        if ct['type'] not in ['html']:
            svgoutputlist += '<g transform="translate(%s,%s)">'%(ct['args']['x'],ct['args']['y'])
            svgoutputlist += ct['rendered']['svg']

            #add a box around groups
            if document._text_box and ct['type'] == 'group':
                svgoutputlist +="""<rect x="0"  y="0" width="%s" height="%s" style="stroke:#009900;stroke-width: 1;stroke-dasharray: 10 5;fill: none;" />"""%(ct['args']['width'],ct['args']['height'])

            svgoutputlist += '</g>'

    return svgoutputlist, animationoutputlist, htmloutputlist, cpt_anim

def place_content(contents, layer_height, layer_width, xtop=0, all_height = {}):
    """
    function to place all contents correctly, do the centering and repartition
    on page and conpute x,y when we enter relative position
    """

    #If we have content with auto y position
    #we compute y anchor of each content
    #height space left
    available_height =  layer_height - xtop

    if all_height != {}:
        #height off all contents
        total_content_height = sum([all_height[a] for a in all_height])

        #Compute the equal space between each elements
        if total_content_height < available_height:
            hspace = (available_height - total_content_height)/float( len(all_height) + 1 )
        else:
            hspace = 0

        #print available_height, total_content_height, hspace
        #compute the y position for each elements
        cpth = xtop + hspace
        for elem in all_height:
            contents[elem]['args']['y'] = "%0.1f"%cpth

            #Print message if overflow
            if cpth >= document._height:
                print("[WARNING] element overflow in height in slide")
                print(cpth, hspace, all_height)

            #Add the element height and hspace to the counter
            cpth += all_height[elem] + hspace

    #Place relative contents and center horizontally
    prevx = xtop
    prevy = 0
    cur_group_x = None
    cur_group_y = None
    cur_group_id = None
    for ct in contents:
        if 'rendered' in ct:
            content = ct['rendered']
        if 'renderedgroup' in ct:
            content = ct['renderedgroup']

        if ('rendered' in ct) or ('renderedgroup' in ct):

            #If it's an html element an it's in a group add group_x group_y to tmpx tmpy
            if ('html' in ct['type']) and ('renderedgroup' in ct) and (ct['renderedgroup']['group_id'] == cur_group_id):
                #print cur_group_x, cur_group_y
                ct['args']['x'] = "%0.1f"%( float(ct['args']['x']) + float(cur_group_x))
                ct['args']['y'] = "%0.1f"%( float(ct['args']['y']) + float(cur_group_y))


            tmpx = ct['args']['x']
            tmpy = ct['args']['y']

            #Check if we need to center horizontaly the content
            if tmpx == 'center':
                tmpx = "%0.1f"%(horizontal_centering(content['width'], 0,  layer_width))
            #same vertically
            if tmpy == 'center':
                tmpy = "%0.1f"%(horizontal_centering(content['height'], xtop,  available_height))

            #check if it's relative positioning of an element, if so add prevx or prevy to element x, y
            if '+' in tmpx:
                tmpx = "%0.1f"%( prevx + float(convert_unit(tmpx.replace('+',''))) )
            if '+' in tmpy:
                tmpy = "%0.1f"%( prevy + float(convert_unit(tmpy.replace('+',''))) )

            #Contert tmpx and tmpy to pixels
            tmpy = convert_unit(tmpy)
            tmpx = convert_unit(tmpx)

            #Store tmpx and tmpy back to the content x, y variables
            ct['args']['x'] = tmpx
            ct['args']['y'] = tmpy

            #print tmpx, tmpy
            #Compute the next prevx and prevy
            prevx = float(tmpx) + content['width']
            prevy = float(tmpy) + content['height']



            #Check if a group have just been placed
            #If a group have been rendered take is x, and y to add to bokeh and html elements
            if 'group' in ct['type']:
                cur_group_x = ct['args']['x']
                cur_group_y = ct['args']['y']
                cur_group_id = ct['args']['group_id']

def render_group(groupsvgs, args):
    """
        group render
    """

    return groupsvgs, float(args['width']), float(args['height'])

