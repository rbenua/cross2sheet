import unittest
from cross2sheet.image import ImageGrid
from cross2sheet.transforms import outside_bars
from urllib.request import urlopen
from io import StringIO

def grid_to_string(l):
    i = StringIO()
    oldr=0
    for r,_,e in l:
        if r>oldr:
            oldr=r
            i.write('\n')
        if e.color==0:
            i.write('#')
        elif e.color==0xffffff:
            i.write('.')
        else:
            i.write('O')
    return i.getvalue()

def bars_to_string(l):
    ymax=max(y for y,_,_ in l)
    xmax=max(x for _,x,_ in l)
    grid=[[' ' for x in range(2*xmax+3)] for y in range(2*ymax+3)]
    for y,x,b in l:
        for c in b.dirs:
            if c=='T':
                grid[2*y][2*x]='+'
                grid[2*y][2*x+1]='-'
                grid[2*y][2*x+2]='+'
            elif c=='L':
                grid[2*y][2*x]='+'
                grid[2*y+1][2*x]='|'
                grid[2*y+2][2*x]='+'
            elif c=='B':
                grid[2*y+2][2*x]='+'
                grid[2*y+2][2*x+1]='-'
                grid[2*y+2][2*x+2]='+'
            elif c=='R':
                grid[2*y][2*x+2]='+'
                grid[2*y+1][2*x+2]='|'
                grid[2*y+2][2*x+2]='+'
    return '\n'.join(''.join(r) for r in grid)

class ImageTest(unittest.TestCase):

    def setUp(self):
        req=urlopen('http://web.mit.edu/puzzle/www/'+self.url)
        data=req.read()
        req.close()
        self.img=ImageGrid(data)
        self.maxDiff=None

    def test_all(self):
        detected=(len(self.img.breaks[0])-1,len(self.img.breaks[1])-1)
        expected=(self.rows,self.cols)
        self.assertEqual(expected,detected,'wrong dimensions')
        if hasattr(self,'fill'):
            with self.subTest('fill'):
                f=grid_to_string(self.img.read_background())
                self.assertEqual(self.fill.strip(),f.strip())
        if hasattr(self,'bars'):
            with self.subTest('bars'):
                grid=self.img.grid()
                grid.features.extend(self.img.read_bars())
                grid.features.extend(outside_bars(grid))
                b=bars_to_string(grid.features)
                self.assertEqual(self.bars.strip(),b.strip())
