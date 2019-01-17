#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pylab as p
from beampy import *

doc = document(cache=False)
#Turn cache to True to speed up compilation
#Color for bacground of code

codeback = "#EFEFEF"

with slide( ):
    maketitle('Beampy a tool to make simple presentation',('Hugo Chauvet',), 'Univ. of python', 'HTML5 presentation' )

with slide():
    title("Text")
    text(r"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$""")

    with group(width=700, height=90, background=codeback):
        code(r"""
    with slide():
        title("Text")
        text(r\"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$\""")
        """, language="python", width=530, x="1cm")



with slide('Figure'):
    figure("./svg_anims/test_0.svg", width=500)
    with group(width=700, height=95, background=codeback):
        code(r"""
    slide("Figure")
    figure("./svg_anims/test_0.svg", width="500")
        """, language="python", width=350, x="1cm")

with slide('Svg animation'):
    animatesvg("./svg_anims/*.svg", width="500")
    with group(width=700, height=95, background=codeback):
        code(r"""
slide('Svg animation')
animatesvg("./svg_anims/*.svg", width="500")
        """, language="python", width=300, x="1cm")



with slide("Matplotlib figure"):
    fig = p.figure()
    x = p.linspace(0,2*p.pi)
    
    p.plot(x, p.sin(x), '--')
    
    figure(fig)



with slide("Matplotlib animation"):

    anim_figs = []
    for i in range(20):
        fig = p.figure()   
        x =  p.linspace(0,2*p.pi)
        p.plot(x, p.sin(x+i))
        p.plot(x, p.sin(x+i+p.pi))
        p.close(fig) 
        anim_figs += [ fig ]
        
        
    animatesvg( anim_figs )


with slide('Video'):
    video("./test.webm", width=500, height=294)
    
    with group(width=700, height=95, background=codeback):
        code(r"""
    slide('Video')
    video("./test.webm", width="500", height="294")
        """, language="python", width="400", x="1cm")
    

with slide('Group and columns'):
    colwidth=350
    with group(width=colwidth, height=doc._height-100, x="1cm", y="1.8cm", background="#000") as g1:
        text("""
    This is a test for a long text in a column style.
    
    $$ \sum_{i=0}^{10} x_i $$
        """, align="center", width=colwidth-20, color="#ffffff")
    
    with group(width=colwidth, height=doc._height-100, x=g1.right+0.01, y=g1.top+0, background=codeback):
        code("""
    slide('Group and columns')
    colwidth=350
    with group(width=colwidth,
        height=doc._height-100,
        x="1cm", y="1.8cm",
        background="#000") as g1:
    
        text(\"""
        This is a test for
        a long text in a
        column style.
    
        $$ \sum_{i=0}^{10} x_i $$
        \""",
        align="center",
        width=colwidth-20,
        color="#ffffff")
        """, width=colwidth-40, language="python", x="0.5cm")




with slide('Relative positioning'):
    text("youpi x=1cm, y=0.1", x="1cm", y=0.1)
    text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
    text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
    
    #text("youpi x=+1cm, y=+0.5cm", x="+1cm", y="+0.5cm")
    #text(r"youpi x=-0, \\ y=+0.5cm", x="-0", y="+0.5cm")
    #text(r"youpi x=+1.5cm,\\ y=-0", x="+1.5cm", y="-0")
    
    with group(width=700, height=195, background=codeback, y="+2.1cm"):
        code(r"""
    slide('Relative positioning')
    text("youpi x=1cm, y=0.1", x="1cm", y=0.1)
    text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
    text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
    
    text("youpi x=+1cm, y=+0.5cm", x="+1cm", y="+0.5cm")
    text(r"youpi x=-0, \\ y=+0.5cm", x="-0", y="+0.5cm")
    text(r"youpi x=+1.5cm,\\ y=-0", x="+1.5cm", y="-0")
        """, language="python", width="450", x="1cm")
    

with slide("Using element's anchors"):
    e0 = text('central element [e0]', y=0.2)
    e1 = text('left of e0', y=e0.top+0, x=e0.left-right(0.1))
    e2 = text('right of e0', y=e0.top+0, x=e0.right+0.1)
    e4 = text('anchors available: top, bottom, center, right, left',
              y=e0.bottom+'1cm', x=e0.center+center(0))
    
    with group(y=e4.bottom+0.15, width=700, height=150, background=codeback):
        code(r"""
    e0 = text('central element [e0]', y=0.2)
    e1 = text('left of e0', y=e0.top+0,
             x=e0.left-right(0.1))
    e2 = text('right of e0', y=e0.top+0, x=e0.right+0.1)
    e4 = text('anchors available: top, bottom, center, right, left',
              y=e0.bottom+'1cm', x=e0.center+center(0))
        """, language="python", width=450, x=0.05)


with slide('Tikz'):
    p = tikz(r"""
     % Local definitions
      \def\costhirty{0.8660256}
    
      % Colors
      \colorlet{anglecolor}{green!50!black}
      \colorlet{sincolor}{red}
      \colorlet{tancolor}{orange!80!black}
      \colorlet{coscolor}{blue}
    
      % Styles
      \tikzstyle{axes}=[]
      \tikzstyle{important line}=[very thick]
      \tikzstyle{information text}=[rounded corners,fill=red!10,inner sep=1ex]
    
      % The graphic
      \draw[style=help lines,step=0.5cm] (-1.4,-1.4) grid (1.4,1.4);
    
      \draw (0,0) circle (1cm);
    
      \begin{scope}[style=axes]
        \draw[->] (-1.5,0) -- (1.5,0) node[right] {$x$};
        \draw[->] (0,-1.5) -- (0,1.5) node[above] {$y$};
    
        \foreach \x/\xtext in {-1, -.5/-\frac{1}{2}, 1}
          \draw[xshift=\x cm] (0pt,1pt) -- (0pt,-1pt) node[below,fill=white]
                {$\xtext$};
    
        \foreach \y/\ytext in {-1, -.5/-\frac{1}{2}, .5/\frac{1}{2}, 1}
          \draw[yshift=\y cm] (1pt,0pt) -- (-1pt,0pt) node[left,fill=white]
                {$\ytext$};
      \end{scope}
    
      \filldraw[fill=green!20,draw=anglecolor] (0,0) -- (3mm,0pt) arc(0:30:3mm);
      \draw (15:2mm) node[anglecolor] {$\alpha$};
    
      \draw[style=important line,sincolor]
        (30:1cm) -- node[left=1pt,fill=white] {$\sin \alpha$} +(0,-.5);
    
      \draw[style=important line,coscolor]
        (0,0) -- node[below=2pt,fill=white] {$\cos \alpha$} (\costhirty,0);
    
      \draw[style=important line,tancolor] (1,0) --
        node [right=1pt,fill=white]
        {
          $\displaystyle \tan \alpha \color{black}=
          \frac{{\color{sincolor}\sin \alpha}}{\color{coscolor}\cos \alpha}$
        } (intersection of 0,0--30:1cm and 1,0--1,1) coordinate (t);
    
      \draw (0,0) -- (t);
    
      \draw[xshift=1.85cm] node [right,text width=6cm,style=information text]
        {
          The {\color{anglecolor} angle $\alpha$} is $30^\circ$ in the
          example ($\pi/6$ in radians). The {\color{sincolor}sine of
            $\alpha$}, which is the height of the red line, is
          \[
          {\color{sincolor} \sin \alpha} = 1/2.
          \]
          By the Theorem of Pythagoras we have ${\color{coscolor}\cos^2 \alpha} +
          {\color{sincolor}\sin^2\alpha} =1$. Thus the length of the blue
          line, which is the {\color{coscolor}cosine of $\alpha$}, must be
          \[
          {\color{coscolor}\cos\alpha} = \sqrt{1 - 1/4} = \textstyle
          \frac{1}{2} \sqrt 3.
          \]%
          This shows that {\color{tancolor}$\tan \alpha$}, which is the
          height of the orange line, is
          \[
          {\color{tancolor}\tan\alpha} = \frac{{\color{sincolor}\sin
              \alpha}}{\color{coscolor}\cos \alpha} = 1/\sqrt 3.
          \]%
        };
    """, figure_options="scale=3,cap=round", x=0.1, y=0.05)
    t = text(r"""
    \href{http://www.texample.net/tikz/examples/tutorial/}{ http://www.texample.net/tikz/examples/tutorial/}
    """, x="center", y=p.bottom+0.05)

    with group(width=700, height=90, background=codeback, y=t.bottom+0.03):
        code(r"""
    slide()
    title('Tikz')
    p = tikz(r\""" ....[TIKZ LINES].... \""")
    t = text(r"\href{http://www.texample.net/tikz/examples/tutorial/}
    {http://www.texample.net/tikz/examples/tutorial/}",
    x="center", y=p.bottom+0.05)
        """, language="python", width="300", x="1cm")



with slide('Bokeh plot'):
    from bokeh.plotting import figure as bokfig
    import numpy as np
    p = bokfig(height=300, width=600)
    x = np.linspace(0, 4*np.pi, 30  )
    y = np.sin(x)
    p.circle(x, y, legend="sin(x)")
    f=figure(p, y=0.1, x="center")

    with group(width=700, height=155, background=codeback, y=f.bottom+0.05):
        code("""
    with slide('Bokeh plot'):
        from bokeh.plotting import figure as bokfig
        import numpy as np
        p = bokfig(height=300, width=600)
        x = np.linspace(0, 4*np.pi, 30  )
        y = np.sin(x)
        p.circle(x, y, legend="sin(x)")
        figure(p, y="+5px", x="center", y=0.1)
        """, language="python", width="300", x="1cm")


save('./beampy_tests.html')
