# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 20:33:18 2015

@author: hugo
"""
from beampy import document
from beampy.functions import gcs, add_to_slide, create_element_id
from beampy.modules.title import title as bptitle
from beampy.geometry import positionner
#Used for group rendering
from beampy.renders import render_content, auto_place_elements, write_content
import sys
from beampy.terminal_output import * #To display beampy messages correctly

class slide():
    """
        Function to add a slide to the presentation
    """

    def __init__(self, title= None, doc = document, style=None):
        #Add a slide to the global counter
        if 'slide' in doc._global_counter:
            doc._global_counter['slide'] += 1
        else:
            doc._global_counter['slide'] = 0
        #Init group counter
        document._global_counter['group'] = 0

        out = {'title':title, 'contents': {},
               'num':doc._global_counter['slide']+1,
               'groups': [],
               'style': style,
               'htmlout': '', #store rendered htmlelements inside the slide
               'animout': [], #store svg rendered part of animatesvg
               'scriptout': '', #store javascript defined in element['script']
               'cpt_anim': 0,
               'element_keys': [] #list to store elements id in order
               }

        self.id = gcs()
        document._contents[self.id] = out

        if title!= None:
            bptitle( title )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def show(self):
        from beampy.exports import display_matplotlib
        display_matplotlib(self.id)

class group():
    """
        Group objects and place the group to a given position on the slide
    """

    def __init__(self, elements_to_group=None, x='center', y='auto', width = None, height = None, background=None):

        if width != None:
            width = width
        if height != None:
            height = height

        self.id = document._global_counter['group']
        self.args = {'group_id': self.id, "background": background}

        self.data = {'args': self.args, 'id': self.id, 'content':'',
                    'render':render_group,'type':'group'}

        self.positionner = add_to_slide(self.data, x, y, width, height)
        document._contents[gcs()]['groups'] += [ self.data ]
        document._global_counter['group'] += 1

        if elements_to_group != None:
            eids = [e.id for e in elements_to_group]
            print("[Beampy][%s] render %i elements in group %i"%(gcs(), len(eids), self.id))
            render_group_content( eids, self.data )

    def __enter__(self):
        #get the position of the first element
        content_start = len(document._contents[gcs()]['contents'])
        #Add it to the data dict
        self.data['content_start'] = content_start

        return self.positionner

    def __exit__(self, type, value, traceback):

        #link the current slide
        slide = document._contents[gcs()]
        if len(slide['groups']) > self.id:
            #Get the last group
            group = slide['groups'][self.id]
            group['content_stop'] = len(slide['contents'])
            elementids = slide['element_keys'][group['content_start']:group['content_stop']]

            print("[Beampy][%s] render %i elements in group %i"%(gcs(), len(elementids), self.id))

            #render the content of a given group
            render_group_content(elementids, self.data)

        else:
            print('The begining of the group as not been defined')
            print(slide['groups'])
            sys.exit(0)

def begingroup(**kwargs):
    """
       start a group
    """
    print('DEPRECATED usage of begingroup ... use with group(...): instead')
    gp = group(**kwargs)
    gp.data['gp'] = gp
    return gp.__enter__()

def endgroup():
    """
        close the current group then computre the height and width of the group
    """
    slide = document._contents[gcs()]
    if len(slide['groups']) > 0:
        slide['groups'][-1]['gp'].__exit__(None,None,None)

def render_group_content(content_ids, group):
    """
        Function to render each elements inside one group defined by their id in content_ids
    """

    #link the current slide
    slide = document._contents[gcs()]
    #Add the group id to all the elements in this group
    cptcache = 0
    groupsid = content_ids

    #print(groupsid)

    #First loop render elements in group
    allwidth = []
    allheight = []
    for k in groupsid:
        elem = slide['contents'][k]
        #Add group id to the element
        elem['group_id'] = group['positionner'].id
        #Render the element or read rendered svg from cache
        cptcache = render_content(elem, cptcache)

        #Get element size
        allwidth += [elem['positionner'].width]
        allheight += [elem['positionner'].height+elem['positionner'].y['shift']]


    #Compute group size if needed
    if group['positionner'].width == None:
        group['positionner'].width = max( allwidth )

    if group['positionner'].height == None:
        group['positionner'].height = sum( allheight )

    #Re loop over element to place them
    all_height = {} #To store height of element for automatic placement
    for i, key in enumerate(groupsid):
        elem = slide['contents'][key]
        if elem['positionner'].y['align'] == 'auto':
            all_height[i] = {"height":elem['positionner'].height, "id":key}
        else:
            elem['positionner'].place( (group['positionner'].width, group['positionner'].height) )

        #Check if we have javascript to output
        if 'script' in elem['args']:
            slide['scriptout'] += ct['args']['script']



    #Manage autoplacement
    #print(all_height)
    if all_height != {}:
        auto_place_elements(all_height, (group['positionner'].width, group['positionner'].height),
                            'y', slide['contents'], ytop=0)



    for key in groupsid:
        elem = slide['contents'][key]
        if 'rendered' in elem and elem['type'] not in ['html']:

            #Add rendered content to groupcontent
            group['content'], slide['animout'], slide['htmlout'], slide['cpt_anim'] = write_content(elem,
                                                    group['content'],
                                                    slide['animout'],
                                                    slide['htmlout'],
                                                    slide['cpt_anim'])

            #remove the rendered part from slide content and set render to None
            #slide['contents'].pop(key)
            #slide['element_keys'].pop(slide['element_keys'].index(key))
            slide['contents'][key]['render'] = None #not processed in the next loop
            slide['contents'][key].pop('rendered')


def render_group( ct ):
    """
        group render
    """

    if ct['args']["background"] != None:
        pre_rect = '<rect width="%s" height="%s" style="fill:%s;" />'%(ct['positionner'].width, ct['positionner'].height, ct['args']['background'])
    else:
        pre_rect = ''

    return pre_rect + ct['content']


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
