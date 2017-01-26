# -*- coding: utf-8 -*-
#!/usr/bin/env python

from bs4 import BeautifulSoup
import hashlib
import time

data = open('./text.svg','r').read()

soup = BeautifulSoup(data, 'xml')

glyph_store = {}

def global_glyph_dict( soup_data ):
    global glyph_store

    #Extract defs containing glyphs from the svg file 
    defs = soup_data.find_all('defs',)[0].extract()

    for path in defs.find_all('path'):
        #store the id of the glyph given by dvisvgm
        path_id = path['id']
        #store the bezier coordinates of the glyph
        path_d = path['d']
        hash_id = hashlib.md5(path_d).hexdigest()
        print(path_id)
        
        #check if the glyph is in the store or add it
        if hash_id not in glyph_store:
            #Add the glyph to the store and create a new uniq id for it
            uniq_id = "g_"+str( len(glyph_store) )
            glyph_store[ hash_id ] = {"old_id": path_id, "d": path_d, "id": uniq_id}
            print(uniq_id, path_id)

            #Find all the xlink:href to this glyph in the use part of the svg
            for tag in soup_data.find_all('use', { 'xlink:href':'#%s'%(path_id) }):
                #Change the dvisvgm ref to the new uniq_id ref of the glyph
                tag['xlink:href'] = uniq_id
                
        #print(path_id)
    
    return soup_data

    
def replace_use_id( soupdata ):
    """
        Function to replace 
    """
    
    tags_to_replace = re.findall('id="(.*)"', str(soupdata.find_all('defs')[0]))
    
    
    for cpt, tag in enumerate(tags_to_replace):
        #print(tag)
        #print({'xlink:href': '#%s'%tag})
        #Some use of this defs 
        new_tag = "test_%i"%cpt
        for elem in soupdata.find_all(attrs={'xlink:href': '#%s'%tag}):
            elem['xlink:href'] = "#%s"%new_tag

        #Inside defs get the good one to change
        for elem in soupdata.find_all(attrs={'id': tag}):
            elem['id'] = new_tag
            
            
defs = soup.find_all('defs')
#print(defs.find_all('path',{'id':'g2-100'}) )
replace_use_id( soup )

#Le extract enleve le noeud du fichier principal
#soup = global_glyph_dict( soup )



#On choppe aussi le group dans lequelle on a les elements
#g1 = soup.find_all('g', {'id':'page1'})[0]
#for i, tag in enumerate(g1.find_all('use')):
#    cur_tag = tag['xlink:href']
#    print(cur_tag)
    #tag['xlink:href'] = 'toto'+str(i)

#print(glyph_store)
