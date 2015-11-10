#!/usr/bin/env python
#-*- coding:utf-8 -*-

from beampy import *

doc = document()

slide()
maketitle('Beampy a tool to make simple presentation','Hugo Chauvet')

slide()
title("Text")
text(r"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$""")

begingroup(width=700, height=90, background="#EFEFEF")
code(r"""
slide()
title("Text")
text(r\"""Use LaTeX to render text and equation \\ $$\sqrt{10}$$\""")
""", langage="python", width="530", x="1cm")
endgroup()

slide()
title('Figure')
figure("./svg_anims/test_0.svg", width="500")
begingroup(width=700, height=95, background="#EFEFEF")
code(r"""
slide()
title("Figure")
figure("./svg_anims/test_0.svg", width="500")
""", langage="python", width="350", x="1cm")
endgroup()

slide()
title('Svg animation')
animatesvg("./svg_anims/", width="500")
begingroup(width=700, height=95, background="#EFEFEF")
code(r"""
slide()
title('Svg animation')
animatesvg("./svg_anims/", width="500")
""", langage="python", width="300", x="1cm")
endgroup()

slide()
title('Video')
video("./test.webm", width="500", height="294")
begingroup(width=700, height=95, background="#EFEFEF")
code(r"""
slide()
title('Video')
video("./test.webm", width="500", height="294")
""", langage="python", width="400", x="1cm")
endgroup()

slide()
title('Group and columns')
colwidth=350
begingroup(width=colwidth, height=doc._height-100, x="1cm", y="1.8cm", background="#000")
text("""
This is a test for a long text in a column style. 

$$ \sum_{i=0}^{10} x_i $$ 
""", align="center", width=colwidth-20, color="#ffffff")
endgroup()
begingroup(width=colwidth, height=doc._height-100, x="430", y="1.8cm", background="#EFEFEF")
code("""
slide()
title('Group and columns')
colwidth=350

begingroup(width=colwidth, 
        height=doc._height-100, 
        x="1cm", 
        y="1.8cm",
        background="#000")
        
text(\"""This is a test for
 a long text in a column style. 

$$ \sum_{i=0}^{10} x_i $$ 
\""", align="center",
width=colwidth-20,
color="#ffffff")

endgroup()
""", width=colwidth-40, langage="python", x="0.5cm")
endgroup()



slide()
title('Relative positioning')
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")

text("youpi x=+1cm, y=+0.5cm", x="+1cm", y="+0.5cm")
text(r"youpi x=-1.5cm,\\ y=+0.5cm", x="-1.5cm", y="+0.5cm")
text(r"youpi x=+1.5cm,\\ y=+0cm", x="+1.5cm", y="+0cm")

begingroup(width=700, height=195, background="#EFEFEF", y="+2.5cm")
code("""
slide()
title('Relative positioning')
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=1cm, y=+0.5cm", x="1cm", y="+0.5cm")
text("youpi x=+1cm, y=+0.5cm", x="+1cm", y="+0.5cm")
text(r"youpi x=-1.5cm,\\ y=+0.5cm", x="-1.5cm", y="+0.5cm")
text(r"youpi x=+1.5cm,\\ y=+0cm", x="+1.5cm", y="+0cm")
""", langage="python", width="450", x="1cm")
endgroup()

slide()
title('Tikz')

tikz(r"""
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
""", figure_options="scale=3,cap=round", x="+3cm", y="+5px")
text(r"""
\textit{http://www.texample.net/tikz/examples/tutorial/}
""", x="center", y="+3cm")
begingroup(width=700, height=90, background="#EFEFEF", y="+20px")
code(r"""
slide()
title('Tikz')
tikz(r\""" ....[TIKZ LINES].... \""")
""", langage="python", width="300", x="1cm")
endgroup()


slide()
title('Bokeh plot')
from bokeh.plotting import figure as bokfig
import numpy as np
p = bokfig(height=300, width=600)
x = np.linspace(0, 4*np.pi, 30  )
y = np.sin(x)
p.circle(x, y, legend="sin(x)")
figure(p, y="+5px", x="center")

begingroup(width=700, height=155, background="#EFEFEF", y="11cm")
code("""
slide()
title('Bokeh plot')
from bokeh.plotting import figure as bokfig
import numpy as np
p = bokfig(height=300, width=600)
x = np.linspace(0, 4*np.pi, 30  )
y = np.sin(x)
p.circle(x, y, legend="sin(x)")
figure(p, y="+5px", x="center")
""", langage="python", width="300", x="1cm")
endgroup()

save('./beampy_tests.html')
