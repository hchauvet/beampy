# coding: utf-8
from beampy.document import document
from beampy.modules.core import beampy_module, group
from beampy.modules.text import text
from beampy.modules.svg import circle, rectangle
from beampy.geometry import center
from beampy.functions import set_curentslide, set_lastslide, render_texts


class tableofcontents(group):
    """Create the table of content for your presentation.
    This function print the TOC tree as defined in your presentation by
    the functions: section(), subsection(), subsubsection()

    Parameters
    ----------
    
    sections : list of section number or int, optional
        List of sections to be displayed (the default is an empty list
        which displays all the section in the TOC). If an integer is
        given, only the given section is displayed.

    subsection : boolean, optional
        Display subsections (the default is True). 
    
    subsubsection : boolean, optional
        Display the subsubsections (the default is True).

    currentsection : boolean, optional
        Highlight the current section (the default is False). When
        True, all other section (and their subsections/subsubsections)
        are shaded with the *hidden_opacity* value, except for the
        subsections/subsubsections of the current section.
    
    currentsubsection : boolean, optional
        Highlight the current subsection (the default is False). Same
        as *currentsection* except that the subsection/subsubsection
        not already presented are also shaded.

    hideothersubsection : boolean, optional
        Hide all the subsections/subsubsections of the section other
        than the current one (the default is False).

    x : int or float or {'center', 'auto'} or str, optional
        Horizontal position for the TOC (the default theme sets this
        to '25px').  See positioning system of Beampy.

    y : int or float or {'center', 'auto'} or str, optional
        Vertical position for the TOC (the default theme
        set this to 'center'). See positioning system of Beampy.

    width : int or float or None, optional
       Width of the TOC (the default is None, which implies that the
       width is the parent group with).

    height : int or float or None, optional
       Height of the TOC (the default is None, which implies that the
       heihgt is the parent group height)

    section_yoffset : int or float, option
       The vertical offset in pixel between two sections (the default theme
       sets this value to 50).

    subsection_xoffset : int or float, optional
       The horizontal offset in pixel between the section and its subsections
       (the default theme sets this to 20). For subsubsections the
       xoffset = 2 * subsection_xoffset.

    subsection_yoffset : int or float, optional
       The vertical offset in pixel between subsections. (the default
       theme sets this to 10).

    section_style : {'round','square','number'} or None, optional
       The decoration displayed in front of the sections. (the default
       theme sets this to 'round').
       
       Possible decorcations are:
       - 'round', display a circle of radius *section_decoration_size*
         filled with *section_decoration_color* color.
       - 'square', display a circle of length *2 x section_decoration_size*
         filled with *section_decoration_color* color.
       - 'number', display section number with the color *section_number_color*
       - None, display nothing.

    subsection_style : {'round','square','number'} or None, optional
       The decoration displayed in front of the subsections. (the default
       theme sets this to None).
       
       Possible decorcations are:
       - 'round', display a circle of radius *subsection_decoration_size*
         filled with *subsection_decoration_color* color.
       - 'square', display a circle of length *2 x subsection_decoration_size*
         filled with *subsection_decoration_color* color.
       - 'number', display section number with the color
         *subsection_text_color*
       - None, display nothing.

    section_decoration_color : string, option
       Section decoration color (the default theme sets this to
       THEME['title']['color']).

    section_decoration_size : int or float, optional
       Section decoration size in pixel (the default theme sets this to 13).

    section_number_color : string, optional
       Section number color (the default theme sets this to 'white').

    section_text_color : string, optional
       Section text color (the default theme sets this to
       THEME['title']['color']).

    subsection_text_color : string, optional
       Subsection text color (the default theme sets this to
       THEME['text']['color']).

    subsection_decoration_color : string, optional
       Subsection decoration color (the default theme sets this to 'gray').

    subsection_decoration_size : int or float, optional
       Subsection decoration size in pixel (the default theme sets
       this to 13/2).

    hidden_opacity : float, optional
       Hidden element opacity (the default theme sets this to
       0.2). Opacity is between 0 (fully hidden) to 1.

    """
    
    def __init__(self, sections=[], subsection=True,
                 subsubsection=True, currentsection=False,
                 currentsubsection=False, hideothersubsection=False,
                 **kwargs):


        self.check_args_from_theme(kwargs)
        super(tableofcontents, self).__init__(x=self.x, y=self.y,
                                              width=self.width,
                                              height=self.height,
                                              opengroup=False)
        
        self.show_subsection = subsection
        self.currentsection = currentsection
        self.currentsubsection = currentsubsection
        self.hideothersubsection = hideothersubsection
        self.sections = sections
        
        if not isinstance(self.sections, list):
            self.sections = [self.sections]
            
        if not subsection:
            self.show_subsubsection = False
        else:
            self.show_subsubsection = subsubsection

        # Store default show options to restaure them in the build_toc_tree
        self.default_show_subsubsection = self.show_subsubsection
        self.default_show_subsection = self.show_subsection
        self.show_section = True

    def build_toc_tree(self):

        set_curentslide(self.slide_id)
        oldtheme = document._theme['link']
        document._theme['link']['fill'] = 'black'
        
        secyoffset = self.section_yoffset
        xoffset = self.subsection_xoffset
        yoffset = self.subsection_yoffset
        
        if self.currentsection or self.currentsubsection:
            vispos = get_visibles_indices(self.slide_id, self.currentsection)
            hidden_opacity = self.hidden_opacity
        else:
            vispos = []
            hidden_opacity = 1
            
        # print('Position in toc %s' % str(vispos))
        opacity = 1
        text_elements = []
        
        with self:
            
            cpt_section = 1
            prev = None
            section = None
                
            for i, node in enumerate(document._TOC):
                
                if node['slide'] <= document._global_counter['slide']:
                    slidelink = '#%i-0' % (node['slide'])
                else:
                    slidelink = '#%i-0' % (document._global_counter['slide'])

                if i in vispos:
                    opacity = 1
                else:
                    opacity = hidden_opacity

                if node['level'] == 0 and len(self.sections) > 0:
                    if cpt_section in self.sections:
                        self.show_section = True
                    else:
                        self.show_section = False
                        cpt_section += 1
                        
                if self.show_section:
                    # Section
                    if node['level'] == 0:
                        cpt_subsection = 1
                        if prev is not None:
                            y = prev.bottom + secyoffset
                        else:
                            y = 0
        
                        if self.hideothersubsection:
                            if i in vispos:
                                self.show_subsection = self.default_show_subsection
                                self.show_subsubsection = self.default_show_subsubsection
                            else:
                                self.show_subsection = False
                                self.show_subsubsection = False

                        deco_x = 0
                        deco_y = y
                        if self.section_style in ('round', 'square'):
                            if self.section_style == 'round':
                                c = circle(r=self.section_decoration_size,
                                           x=0, y=y, opacity=opacity,
                                           color=self.section_decoration_color,
                                           edgecolor=self.section_decoration_color)
                            else:
                                c = rectangle(width=self.section_decoration_size*2,
                                              height=self.section_decoration_size*2,
                                              x=0, y=y, opacity=opacity,
                                              color=self.section_decoration_color,
                                              edgecolor=self.section_decoration_color)
                        
                            tt = text(r'\textbf{%i}' % cpt_section,
                                      x=c.center+center(0),
                                      y=c.center+center(0),
                                      color=self.section_number_color,
                                      size=self.section_decoration_size)

                            text_elements += [tt]

                            deco_x = c.right + 5
                            deco_y = c.center + center(0)

                        if self.section_style == 'number':
                            c = text(r'\textbf{%i}' % cpt_section,
                                     x=0, y=y,
                                     color=self.section_number_color,
                                     size=self.section_decoration_size)

                            text_elements += [c]
                            
                            deco_x = c.right + 5
                            deco_y = c.center + center(0)
                            
                        prev = text(r'\href{%s}{%s}' % (slidelink, node['title']),
                                    x=deco_x, y=deco_y,
                                    color=self.section_text_color, opacity=opacity,
                                    width=document._slides[self.slide_id].curwidth - (self.section_decoration_size*2+5))
                        text_elements += [prev]
                        
                        section = prev
                        cpt_section += 1

                if self.show_subsection and self.show_section:
                    # Subsection

                    if node['level'] == 1:
                        cpt_subsubsection = 1
                        x = node['level'] * xoffset
                        if section is not None:
                            x = section.left + x
                            
                        if prev is not None:
                            y = prev.bottom+yoffset
                        else:
                            y = 0

                        deco_x = x
                        deco_y = y
                        if self.subsection_style == 'number':
                            c = text('%i-%i' % (cpt_section-1, cpt_subsection),
                                     x=x, y=y,
                                     color=self.subsection_text_color)

                            text_elements += [c]
                            
                            deco_x = c.right + 5
                            deco_y = c.center + center(0)
                            
                        if self.subsection_style in ('round', 'square'):
                            if self.subsection_style == 'round':
                                c = circle(r=self.subsection_decoration_size,
                                           x=x, y=y, opacity=opacity,
                                           color=self.subsection_decoration_color,
                                           edgecolor=self.subsection_decoration_color)
                            else:
                                c = rectangle(width=self.subsection_decoration_size*2,
                                              height=self.subsection_decoration_size*2,
                                              x=x, y=y, opacity=opacity,
                                              color=self.subsection_decoration_color,
                                              edgecolor=self.subsection_decoration_color)
                        
                            deco_x = c.right + 5
                            deco_y = c.center + center(0)
                            
                        prev = text(r'\href{%s}{%s}' % (slidelink, node['title']),
                                    x=deco_x, y=deco_y, opacity=opacity,
                                    color=self.subsection_text_color)

                        text_elements += [prev]
                        
                        cpt_subsection += 1

                if self.show_subsubsection and self.show_section:
                    # Subsubsection
                    if node['level'] == 2:
                        x = node['level'] * xoffset
                        if section is not None:
                            x = section.left + x
      
                        if prev is not None:
                            y = prev.bottom+yoffset
                        else:
                            y = 0

                        deco_x = x
                        deco_y = y
                        if self.subsection_style == 'number':
                            c = text('%i-%i-%i' % (cpt_section-1, cpt_subsection-1,
                                                   cpt_subsubsection),
                                     x=x, y=y,
                                     color=self.subsection_text_color)
                            
                            text_elements += [c]
                            
                            deco_x = c.right + 5
                            deco_y = c.center + center(0)

                        if self.subsection_style in ('round', 'square'):
                            if self.subsection_style == 'round':
                                c = circle(r=self.subsection_decoration_size,
                                           x=x, y=y, opacity=opacity,
                                           color=self.subsection_decoration_color,
                                           edgecolor=self.subsection_decoration_color)
                            else:
                                c = rectangle(width=self.subsection_decoration_size*2,
                                              height=self.subsection_decoration_size*2,
                                              x=x, y=y, opacity=opacity,
                                              color=self.subsection_decoration_color,
                                              edgecolor=self.subsection_decoration_color)
                        
                            deco_x = c.right + 5
                            deco_y = c.center + center(0)
                        
                        prev = text(r'\href{%s}{%s}' % (slidelink, node['title']),
                                    x=deco_x, y=deco_y, opacity=opacity,
                                    color=self.subsection_text_color)

                        text_elements += [prev]
                        
                        cpt_subsubsection += 1

        set_lastslide()
        document._theme['link'] = oldtheme

        return text_elements
        
    def pre_render(self):

        #print('build toc tree')
        text_elements = self.build_toc_tree()
        render_texts(text_elements)
        # Need to update visible layers
        self.propagate_layers()
        

def get_visibles_indices(slide_id, currentsection=False):

    currenttoc = document._slides[slide_id].TOCposition
    tocposition = document._TOC.index(currenttoc)
    currentlevel = currenttoc['level']

    visiblespos = [tocposition]

    while currentlevel != 0 and tocposition > 0:
        tocposition -= 1
        currentlevel = document._TOC[tocposition]['level']
        visiblespos += [tocposition]

    # Case where all subsection of a section need to be shown
    if currentsection:
        max_visiblepos = max(visiblespos)
        maxlevel = document._TOC[max_visiblepos]['level']

        while maxlevel != 0 and max_visiblepos < len(document._TOC)-1:
            max_visiblepos += 1
            maxlevel = document._TOC[max_visiblepos]['level']
            if maxlevel != 0:
                visiblespos += [max_visiblepos]

    return visiblespos
