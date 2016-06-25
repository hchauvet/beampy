# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 20:33:18 2015

@author: hugo
"""
from beampy import document
from beampy.functions import (gcs, create_element_id,
 check_function_args, get_command_line, convert_unit,
 pre_cache_svg_image, print_function_args)


from beampy.geometry import positionner
#Used for group rendering
from beampy.slide_render_functions import  auto_place_elements
import sys
import time

class slide():
    """
        Function to add a slide to the presentation
    """

    def __init__(self, title= None, **kwargs):

        #Add a slide to the global counter
        if 'slide' in document._global_counter:
            document._global_counter['slide'] += 1
        else:
            document._global_counter['slide'] = 0
        #Init group counter
        document._global_counter['group'] = 0

        #check args from THEME
        self.args = check_function_args(slide, kwargs)

        out = {'title':title,
               'contents': {},
               'num':document._global_counter['slide']+1,
               'groups': [],
               "args": self.args,
               'htmlout': '', #store rendered htmlelements inside the slide
               'animout': [], #store svg rendered part of animatesvg
               'scriptout': '', #store javascript defined in element['script']
               'cpt_anim': 0,
               'element_keys': [] #list to store elements id in order
               }

        #The id for this slide
        self.id = gcs()


        #Change from dict to class
        self.tmpout = out
        self.contents = out['contents']
        self.element_keys = out['element_keys']
        self.cpt_anim = 0
        self.num = out['num']
        self.title = title

        #Store all outputs
        self.svgout = []
        self.htmlout = []
        self.scriptout = []
        self.animout = []
        self.svgheader = ''
        self.svgfooter = '\n</svg>\n'

        self.cpt_anim = 0
        self.groups = []

        #Add the slide to the document contents list
        document._contents[self.id] = out
        document._slides[self.id] = self

        if title!= None:
            from beampy.modules.title import title as bptitle
            bptitle( title )
            self.ytop = float(convert_unit(self.title.reserved_y))
        else:
            self.ytop = 0


    def add_module(self, module_id, module_content):
        #Add a module to the current slide
        self.element_keys += [module_id]
        self.contents[module_id] = module_content

    def remove_module(self, module_id):
        #Remove a module
        self.element_keys.pop(self.element_keys.index(module_id))
        self.contents.pop(module_id)

    def add_rendered(self, svg=None, html=None, js=None, animate_svg=None):

        if svg != None:
            self.svgout += [svg]

        if html != None:
            self.htmlout += [html]

        if js != None:
            self.scriptout += [js]

        if animate_svg != None:
            self.animout += [animate_svg]


    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def show(self):
        from beampy.exports import display_matplotlib
        display_matplotlib(self.id)

    def render(self):
        """
            Function to render a slide to an svg figure
        """

        pre = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
        """

        print( '-'*20 + ' slide_%i '%self.num + '-'*20 )

        out = pre+"""\n<svg width='%ipx' height='%ipx' style='background-color: "%s";'
        xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:cc="http://creativecommons.org/ns#"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        >"""%(document._width, document._height, self.args['background'])

        #Add the svg header to svg dict of the slide
        self.svgheader = out
        #self.add_rendered( svg=out )

        #Run render of each elements
        t = time.time()
        for i, ct in self.contents.iteritems():
            if not ct.rendered:
                ct.run_render()
            #print ct.keys()

        print('Rendering elements in %0.3f sec'%(time.time()-t))

        t = time.time()

        #Place contents that's are not inside groups
        htmlingroup = []
        all_height = {}
        for cpt, i in enumerate(self.element_keys):
            ct = self.contents[i]

            if ct.group_id != None:
                #Check if it's an html inside one group
                if ct.type == 'html':
                    htmlingroup += [i]

            else:
                if ct.type != None:
                    #print(ct['type'])
                    #Check if it's a group
                    #if ct.type == 'group':
                        #render the group
                    #    ct.run_render()

                    #Check if it's an auto placement or we can place the element
                    if ct.positionner.y['align'] == 'auto':
                        all_height[cpt] = {"height": ct.positionner.height, "id":i}
                    else:
                        ct.positionner.place( (document._width, document._height), ytop=self.ytop )


        #Manage auto placement
        if all_height != {}:
            auto_place_elements(all_height, (document._width, document._height),
                                'y', self.contents, self.ytop)

        #Extra operations for html contents
        if htmlingroup != []:
            for i in htmlingroup:
                ct = self.contents[i]
                #add off set to the html div position
                group = self.groups[ ct.group_id ]
                ct.positionner.x['final'] += group.positionner.x['final']
                ct.positionner.y['final'] += group.positionner.y['final']

        #Store rendered contents in svgout, htmlout, jsout
        for key in self.element_keys:
            ct = self.contents[key]


            if ct.group_id == None:
                svgo = None
                htmlo = None
                animo = None
                jso = None

                if ct.svgout != None:
                    svgo = ct.export_svg()

                if ct.htmlout != None:
                    htmlo = ct.export_html()

                if ct.animout != None:
                    svgo, animo = ct.export_animation()

                if ct.jsout != None:
                    jso = ct.jsout

                self.add_rendered(svgo, htmlo, jso, animo)

            #For group we need to output html even if the elem is in one group
            #(html is absolute positionning see line 180 just above)
            else:
                if ct.htmlout != None:
                    htmlo = ct.export_html()
                    self.add_rendered(html=htmlo)

        #Add grid and fancy stuff...
        if document._guide:
            available_height = document._height - self.ytop
            out = ''
            out += '<g><line x1="400" y1="0" x2="400" y2="600" style="stroke: #777"/></g>'
            out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>'%(self.ytop + available_height/2.0, self.ytop + available_height/2.0)
            out += '<g><line x1="0" y1="%0.1f" x2="800" y2="%0.1f" style="stroke: #777"/></g>'%(self.ytop, self.ytop)
            self.add_rendered(svg=out)


        #Close the main svg
        #self.add_rendered( svg="\n</svg>\n" )

        print('Placing elements in %0.3f'%(time.time()-t))

class beampy_module():
    """
        Base class for creating a module

        Each module need a render method and need to return a register
    """

    rendered = False #State of the module (True if it has been rendered to an svg
    positionner = None #Store the positionner (to manage placement in slide)
    content = None #Store the input content
    type = None #Define the type of the module
    name = None
    args = None #Store the raw dict of passed args (see check_args_from_theme)

    #Storage of render outputs
    svgout = None #The output of the render
    htmlout = None #We can store also html peace of code
    jsout = None #Store javascript if needed
    animout = None #Store multiple rasters for animation

    call_cmd = '' #Store the command used in the source script
    call_lines = '' #Store lines of the call cmd
    id = None #store a unique id for this module
    group_id = None #store the group id if the module is inside one group

    #Needed args (give some default one)
    x = 0
    y = 0
    width = None
    height = None

    #Special args used to create cache id from md5
    args_for_cache_id = None
    #Do cache for this element or not
    cache = True

    #Save the id of the current slide for the module
    slide_id = None

    def __init__(self, **kargs):

        self.check_args_from_theme(kargs)
        self.register()
        print("Base class for a new module")


    def register(self):
        #Function to register the module (run the function add to slide)

        #Save the id of the current slide for the module
        self.slide_id = gcs()

        #Ajout du nom du module
        self.name = self.get_name()

        #Create a unique id for this element
        self.id = create_element_id( self )

        #print(elem_id)
        document._slides[self.slide_id].add_module(self.id, self)

        self.positionner = positionner( self.x, self.y , self.width, self.height, self.id)

        #Add anchors for relative positionning
        self.top = self.positionner.top
        self.bottom = self.positionner.bottom
        self.left = self.positionner.left
        self.right = self.positionner.right
        self.center = self.positionner.center

        #Report width, height from positionner to self.width, self.height
        self.width = self.positionner.width
        self.height = self.positionner.height

        #Add the source of the script that run this module
        start, stop, source = get_command_line( self.name )
        self.call_cmd = source
        self.call_lines = (start, stop)

    def delete(self):
        #Remove from document
        document._slides[gcs()].remove_module(self.id)
        del self

    def render(self):
        #Define the render for this module (how it is translated to an svg (or html element))

        #If the width/height changes ... update them!
        #self.update_size(new_width, new_height)

        #Store your the render outputs to
        self.svgout = None
        self.htmlout = None
        self.jsout = None
        self.animout = None

    def run_render(self):
        """
            Run the function self.render if the module is not in cache
        """

        #Get the current slide object
        slide = document._slides[gcs()]

        if self.cache and document._cache != None:
            ct_cache = document._cache.is_cached('slide_%i'%slide.num, self)
            if ct_cache:
                #Update the state of the module to rendered
                self.rendered = True
                try:
                    print("Elem [%s ...] from cache"%self.call_cmd.strip()[:20])
                except:
                    print("Elem %s from cache"%self.name)
            else:
                #print("element %i not cached"%ct['positionner'].id)
                self.render()
                document._cache.add_to_cache('slide_%i'%slide.num, self)
                try:
                    print("Elem [%s ...] rendered"%self.call_cmd.strip()[:20])
                except:
                    print("Elem %s rendered"%self.name)
        else:
            self.render()
            try:
                print("Elem [%s ...] rendered"%self.call_cmd.strip()[:20])
            except:
                print("Elem %s rendered"%self.name)

    def get_name(self):
        #Return the name of the module
        return str(self.__init__.im_class).split('.')[-1]

    def check_args_from_theme(self, arg_values_dict):
        """
            Function to check input function args.

            Functions args are defined in the default_theme.py
            or if a theme is added the new value is taken rather than the default one
        """

        #Add args value to the module
        self.args = arg_values_dict

        function_name = self.get_name()
        default_dict = document._theme[function_name]
        outdict = {}
        for key, value in arg_values_dict.items():
            #Check if this arguments exist for this function
            if key in default_dict:
                outdict[key] = value
                setattr(self, key, value)
            else:
                print("Error the key %s is not defined for %s module"%(key, function_name))
                print_function_args(function_name)
                sys.exit(1)

        #Check if their is ommited arguments that need to be loaded by default
        for key, value in default_dict.items():
            if key not in outdict:
                setattr(self, key, value)

    def load_extra_args(self, theme_key):
        """
            Function to load default args from the theme for the given theme_key
            and add them to the module
        """
        for key, value in document._theme[theme_key].items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def update_size(self, width, height):
        """
            Update the size (width, height) of the current module
        """

        self.width = width
        self.height = height
        self.positionner.update_size( self.width, self.height )

    def __repr__(self):
        out = 'module: %s\n'%self.name
        try:
            out += 'source (lines %i->%i):\n%s'%(self.call_lines[0], self.call_lines[1],
                                       self.call_cmd)
        except:
            out += 'source : fail\n'

        out += 'width: %s, height: %s\n'%(str(self.width), str(self.height))

        return out

    #Export methods (how the final svg/html/multisvg is written down)
    #add a group/div object with the good x, y, positions

    def export_svg(self):
        out = '<g transform="translate(%s,%s)">'%(self.positionner.x['final'],
                                                  self.positionner.y['final'])

        out += self.svgout

        if document._text_box:
            out +="""<rect x="0"  y="0" width="%s" height="%s" style="stroke:#009900;stroke-width: 1;stroke-dasharray: 10 5;fill: none;" />"""%(self.width, self.height)

        out += '</g>'

        return out

    def export_html(self):

        out = """<div style="visibility: hidden; position: absolute; left: %spx; top: %spx;"> %s </div></br>"""
        out = out%(self.positionner.x['final'], self.positionner.y['final'], self.htmlout)

        return out

    def export_animation(self):
        #Export animation of list of svg
        if type(self.animout) == type(list()):
            #Get the current slide object
            slide = document._slides[self.slide_id]
            #print(self.slide_id, slide.cpt_anim)
            #Pre cache raster images
            frames_svg_cleaned, all_images = pre_cache_svg_image( self.animout )

            #Add an animation to animout dict
            animout = {}
            animout['header'] = "%s"%(''.join(all_images))
            animout['config'] = { 'autoplay':self.autoplay, 'fps': self.fps }
            animout['frames'] = frames_svg_cleaned

            slide_number = int(self.slide_id.split('_')[-1])
            #out = "<defs id='pre_loaded_images_%i'></defs>"%(slide.cpt_anim)
            out = '<g id="svganimate_s%i_%i" transform="translate(%s,%s)" onclick="Beampy.animatesvg(%i,%i,%i);">'%(slide_number,
                    slide.cpt_anim,
                    self.positionner.x['final'],
                    self.positionner.y['final'],
                    slide.cpt_anim, self.fps, len(self.animout))

            #out += '%s'%(''.join(self.animout))
            out += self.animout[0]
            #Link the first frame
            #out += '<g id="display_animation_%i"></g>'%slide.cpt_anim
            out += '</g>'



            #Add +1 to anim counter
            slide.cpt_anim += 1

            return out, animout


class group(beampy_module):
    """
        Group objects and place the group to a given position on the slide
    """

    def __init__(self, elements_to_group=None, x='center', y='auto', width = None, height = None, background=None):

        #Store the input of the module
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.background = background
        self.type = 'group'
        self.content = []
        #TODO: remode these to belows
        #self.args = {'group_id': self.group_id, "background": background}
        #self.data = {'args': self.args, 'id': self.group_id, 'content':'',
        #            'render':render_group,'type':'group'}

        #Add group id from the global group counter
        self.idg = document._global_counter['group']
        document._slides[gcs()].groups += [ self ]
        document._global_counter['group'] += 1

        #Add classic register to the slide
        self.register()

        if elements_to_group != None:
            eids = [e.id for e in elements_to_group]
            print("[Beampy][%s] render %i elements in group %i"%(self.slide_id, len(eids), self.idg))
            self.render_ingroup( eids )


    def __enter__(self):
        #get the position of the first element
        self.content_start = len(document._contents[self.slide_id]['contents'])

        return self.positionner

    def __exit__(self, type, value, traceback):

        #link the current slide
        slide = document._slides[self.slide_id]
        if len(slide.groups) > self.idg:
            #Get the last group
            self.content_stop = len(slide.contents)
            elementids = slide.element_keys[self.content_start:self.content_stop]

            if len(elementids) > 0:
                print("[Beampy][%s] render %i elements in group %i"%(gcs(),
                       len(elementids), self.idg))

                #render the content of a given group
                self.render_ingroup( elementids )

        else:
            print('The begining of the group as not been defined')
            print( slide.groups )
            sys.exit(0)


    def render_ingroup(self, content_ids):
        """
            Function to render each elements inside one group defined by their id in content_ids
        """

        #link the current slide
        slide = document._slides[self.slide_id]

        #Add the group id to all the elements in this group
        cptcache = 0
        groupsid = content_ids

        #First loop render elements in group
        allwidth = []
        allheight = []
        for k in groupsid:
            elem = slide.contents[k]
            #Add group id to the element
            elem.group_id = self.idg
            #Render the element or read rendered svg from cache
            if not elem.rendered:
                elem.run_render()

            #Get element size
            allwidth += [elem.positionner.width]
            allheight += [elem.positionner.height+elem.positionner.y['shift']]


        #Compute group size if needed
        if self.width == None:
            self.width = max( allwidth )
            self.positionner.width = self.width

        if self.height == None:
            self.height = sum( allheight )
            self.positionner.height = sum( allheight )

        #Re loop over element to place them
        all_height = {} #To store height of element for automatic placement
        for i, key in enumerate(groupsid):
            elem = slide.contents[key]
            if elem.positionner.y['align'] == 'auto':
                all_height[i] = {"height":elem.positionner.height, "id":key}
            else:
                elem.positionner.place( (self.width, self.height) )


        #Manage autoplacement
        #print(all_height)
        if all_height != {}:
            auto_place_elements(all_height, (self.width, self.height),
                                'y', slide.contents, ytop=0)

        for key in groupsid:
            elem = slide.contents[key]
            if elem.type not in ['html']:

                if elem.svgout != None:
                    self.content += [ elem.export_svg() ]

                if elem.jsout != None:
                    slide.add_rendered( js=elem.jsout )

                if elem.animout != None:
                    tmpsvg, tmpanim = elem.export_animation()
                    self.content += [tmpsvg]
                    slide.add_rendered(animate_svg=tmpanim)

    def render( self ):
        """
            group render
        """

        if self.background != None:
            pre_rect = '<rect width="%s" height="%s" style="fill:%s;" />'%(self.width,
             self.height, self.background)
        else:
            pre_rect = ''

        self.svgout = pre_rect + ''.join(self.content)
        self.rendered = True

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
