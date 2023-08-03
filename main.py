"""     Simple Tetris using PyGlet  """
"""             July 2023           """
"""      Raymond NGUYEN THANH       """

from enum import IntEnum, unique
import pyglet
from pyglet.window import Window
from pyglet.shapes import Rectangle
from pyglet.window import key
from pyglet import clock
from random import randint
from os import path

# Constants
WIN_WIDTH = 480
WIN_HEIGHT = 560
NB_ROWS = 20
NB_COLUMNS = 10
CELL_SIZE  = int(WIN_WIDTH / (NB_COLUMNS + 9))
OX = CELL_SIZE
OY = 50

@unique
class GameMode(IntEnum):
    StandBy = 1
    Play = 2
    GameOver = 3
    HightScore = 4

@unique
class TetrominoShape(IntEnum):
    
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7

class Tetromino:
    
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    colorsTable = [(0x00,0x00,0x00,0x00),
                    (0xCC,0x66,0x66,0xFF),
                    (0x66,0xCC,0x66,0xFF),
                    (0x66,0x66,0xCC,0xFF),
                    (0xCC,0xCC,0x66,0xFF),
                    (0xCC,0x66,0xCC,0xFF),
                    (0x66,0xCC,0xCC,0xFF),
                    (0xDA,0xAA,0x00,0xFF)]
    
    def __init__(self,x :int ,y :int, shape :int) -> None:
        self.v = [[0,0] for i in range(4)]
        self.x = x
        self.y = y
        self.pieceShape = shape
        self.color = Tetromino.colorsTable[shape]
        self.setShape(shape)
        self.velocityX = 0
        self.velocityY = -1

    def setShape(self, shape):
        '''sets a shape'''
        table = Tetromino.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.v[i][j] = table[i][j]
        self.pieceShape = shape
        self.color = Tetromino.colorsTable[shape]

    def draw(self):
        '''draw Tetromino'''
        rect = Rectangle(100,100,CELL_SIZE-2,CELL_SIZE-2,color=self.color)
        for [vx,vy] in self.v:
            rect.x = self.x + vx*CELL_SIZE + OX + 1
            rect.y = self.y + vy*CELL_SIZE + OY + 1
            rect.draw()

    def rotateLeft(self):
        '''rotate shape to the left'''
        if self.pieceShape == TetrominoShape.SquareShape:
            return
        for id,[vx,vy] in enumerate(self.v):
            self.v[id][0] = vy
            self.v[id][1] = -vx

    def rotateRight(self):
        '''rotate shape to the right'''        
        if self.pieceShape == TetrominoShape.SquareShape:
            return
        for id,[vx,vy] in enumerate(self.v):
            self.v[id][0] = -vy
            self.v[id][1] = vx

    def minX(self)->int:
        '''returns min x value'''
        m = 1000
        for [vx,_] in self.v:
            m = min(m, vx)
        return m
        
    def maxX(self)->int:
        '''returns max x value'''
        m = -1000
        for [vx,_] in self.v:
            m = max(m, vx)
        return m
    
    def minY(self)->int:
        '''returns min y value'''
        m = 1000
        for [_,vy] in self.v:
            m = min(m, vy)
        return m
        
    def maxY(self)->int:
        '''returns max y value'''
        m = -1000
        for [_,vy] in self.v:
            m = max(m, vy)
        return m
    
    def iX(self)->int:
        ix = int((self.x)/CELL_SIZE)
        return ix
    
    def iY(self)->int:
        iy = int((self.y)/CELL_SIZE)
        return iy
    
    def hitGround(self, board: list[int])->bool:
        
        for [vx,vy] in self.v:

            # Top Left
            ix = int((vx*CELL_SIZE + self.x)/CELL_SIZE)
            iy = int((vy*CELL_SIZE + self.y)/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                t = board[ix+NB_COLUMNS*iy]
                if t!=0:
                    return True                        
            # Top Right
            ix = int((vx*CELL_SIZE + self.x + CELL_SIZE - 1)/CELL_SIZE)
            iy = int((vy*CELL_SIZE + self.y)/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                t = board[ix+NB_COLUMNS*iy]
                if t!=0:
                    return True        

            # Bottom Right
            ix = int((vx*CELL_SIZE + self.x + CELL_SIZE - 1)/CELL_SIZE)
            iy = int((vy*CELL_SIZE + self.y + CELL_SIZE - 1)/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                t = board[ix+NB_COLUMNS*iy]
                if t!=0:
                    return True        

            # Bottom Left
            ix = int((vx*CELL_SIZE + self.x)/CELL_SIZE)
            iy = int((vy*CELL_SIZE + self.y + CELL_SIZE -1)/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                t = board[ix+NB_COLUMNS*iy]
                if t!=0:
                    return True        
                
        return False

    def hitLeft(self, board: list[int])->bool:
        self.velocityX = -1
        fHit = False
        for [vx,vy] in self.v:
            x = vx*CELL_SIZE + self.x - 1
            y = vy*CELL_SIZE + self.y
            ix = int(x/CELL_SIZE)
            iy = int(y/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                if board[ix+iy*NB_COLUMNS]!=0:
                    fHit = True
                    break
            y = vy*CELL_SIZE + self.y + CELL_SIZE - 1
            iy = int(y/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                if board[ix+iy*NB_COLUMNS]!=0:
                    fHit = True
                    break
        return fHit
    
    def hitRight(self,board: list[int])->bool:
        fHit = False
        for [vx,vy] in self.v:
            x = vx*CELL_SIZE + self.x + CELL_SIZE
            y = vy*CELL_SIZE + self.y
            ix = int(x/CELL_SIZE)
            iy = int(y/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                if board[ix+iy*NB_COLUMNS]!=0:
                    fHit = True
                    break
            y = vy*CELL_SIZE + self.y + CELL_SIZE - 1
            iy = int(y/CELL_SIZE)
            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                if board[ix+iy*NB_COLUMNS]!=0:
                    fHit = True
                    break
        return fHit

    def isOutLimits(self)->bool:
        for [vx,vy] in self.v:
            x = vx*CELL_SIZE + self.x
            y = vy*CELL_SIZE + self.y
            ix = int(x/CELL_SIZE)
            iy = int(y/CELL_SIZE)
            if (ix<0) or (ix>=NB_COLUMNS) or (iy<0) or (iy>=NB_ROWS):
                return True
        return False
    
    def isOutRightLimit(self)->bool:
        for [vx,vy] in self.v:
            x = vx*CELL_SIZE + self.x
            y = vy*CELL_SIZE + self.y
            ix = int(x/CELL_SIZE)
            iy = int(y/CELL_SIZE)
            if (ix>=NB_COLUMNS):
                return True
        return False            
       
    def isOutLeftLimit(self)->bool:
        for [vx,vy] in self.v:
            x = vx*CELL_SIZE + self.x
            y = vy*CELL_SIZE + self.y
            ix = int(x/CELL_SIZE)
            iy = int(y/CELL_SIZE)
            if (ix<0):
                return True
        return False            

    def hitBottom(self)->bool:
        for [_,vy] in self.v:
            y = vy*CELL_SIZE + self.y+CELL_SIZE
            iy = int(y/CELL_SIZE)
            if iy==0:
                return True
        return False

class HighScore:
    def __init__(self, name:str, score:int):
        self.name = name
        self.score = score

class Fenetre(Window):

    def __init__(self,width,height):
        super().__init__(width,height,vsync=True)
        self.set_caption('Tetris 0.01')
        pyglet.font.add_file('sansation.ttf')
        self.sansation = pyglet.font.load('sansation')
        self.soundSucces = pyglet.resource.media('109662__grunz__success.wav', streaming=False)
        self.soundSucces.volume = 0.05
        self.myplayer = pyglet.media.Player()
        self.myplayer.loop = True
        self.source = pyglet.media.load(filename="Tetris.ogg", streaming=False)
        self.myplayer.queue(self.source)
        self.musicVolume = 3
        self.myplayer.volume = self.musicVolume/10.0
        self.myplayer.play()
        self.mode = GameMode.StandBy
        self.fMusic = False
        self.score = 0
        self.player_name = "XXXXX"
        self.hightScores = [HighScore("--------",0) for i in range(10)]
        self.loadHightScore()
        self.idHightScore = -1
        self.iColorHighScore = 0
        self.board = [0 for i in range(0,NB_COLUMNS*NB_ROWS)]
        self.tetroBag = [1,2,3,4,5,6,7,1,2,3,4,5,6,7]
        self.idTetroBag = 14
        self.curTetromino = Tetromino(5*CELL_SIZE,18*CELL_SIZE,self.tetrisRandomizer())
        self.nextTetromino = Tetromino(13*CELL_SIZE,10*CELL_SIZE,self.tetrisRandomizer())
        self.nbCompletedLines = 0
        self.fDropTetromino = False
        self.fGameOver = False
        self.hVelocity = 0
        self.elapseTime1 = 0
        self.elapseTime2 = 0
        self.elapseTime3 = 0
        self.boardRect = Rectangle(OX,OY,CELL_SIZE*NB_COLUMNS,CELL_SIZE*NB_ROWS,color=(0,0,50,255))
        self.score_label = pyglet.text.Label('SCORE : {:06d}'.format(self.score),font_name='sansation',
                                             font_size=14,bold=True,x=10,y=15,color=(255, 255, 0,255))
        self.tblChars = {
            key.A:'A',
            key.B:'B',
            key.C:'C',
            key.D:'D',
            key.E:'E',
            key.F:'F',
            key.G:'G',
            key.H:'H',
            key.I:'I',
            key.J:'J',
            key.K:'K',
            key.L:'L',
            key.M:'M',
            key.N:'N',
            key.O:'O',
            key.P:'P',
            key.Q:'Q',
            key.R:'R',
            key.S:'S',
            key.T:'T',
            key.U:'U',
            key.V:'V',
            key.W:'W',
            key.X:'X',
            key.Y:'Y',
            key.Z:'Z',
            key.NUM_0:'0',
            key.NUM_1:'1',
            key.NUM_2:'2',
            key.NUM_3:'3',
            key.NUM_4:'4',
            key.NUM_5:'5',
            key.NUM_6:'6',
            key.NUM_7:'7',
            key.NUM_8:'8',
            key.NUM_9:'9',
            key._0:'1',
            key._2:'2',
            key._3:'3',
            key._4:'4',
            key._5:'5',
            key._6:'6',
            key._7:'7',
            key._8:'8',
            key._9:'9'
        }

        # self.board[5] = 3
        # self.board[NB_COLUMNS+5] = 3
        # self.board[2*NB_COLUMNS+5] = 3
        # self.board[3*NB_COLUMNS+5] = 3
        # self.board[4*NB_COLUMNS+5] = 3
        # self.board[5*NB_COLUMNS+5] = 3
        # self.board[6*NB_COLUMNS+5] = 3
        
    def saveHightScore(self):
        with open("highscores.txt",'w',encoding="utf-8") as f:
            for hs in self.hightScores:
                strLi = "{};{}\n".format(hs.name,hs.score)
                f.write(strLi)

    def loadHightScore(self):
        if path.exists("highscores.txt"):
            with open("highscores.txt",'r',encoding="utf-8") as f:
                strLines = f.readlines()
                i = 0
                for strL in strLines:
                    if len(strL)>1:
                        name,score = strL.split(';')
                        self.hightScores[i].name = name
                        self.hightScores[i].score = int(score)
                        i += 1
                        
    def isHightScore(self)->int:
        self.idHightScore = -1
        for i, hs in enumerate(self.hightScores):
            if self.score>hs.score:
                self.idHightScore = i
                return i
        return -1

    def insertHightScore(self, id:int, name:str, score:int):
        if id>=0:
            self.hightScores.insert(id,HighScore(name,score))
            self.hightScores.pop()

    def setHightScoreName(self,name:str):
        if self.idHightScore>=0:
            self.hightScores[self.idHightScore].name = name

    def is_game_over(self)->bool:
        iTop = (NB_ROWS - 1)*NB_COLUMNS
        for x in range(0,NB_COLUMNS):
            if self.board[iTop+x] != 0:
                return True
        return False

    def compute_score(self, nb_lines: int) -> int:
        if nb_lines==1:
            return 40
        elif nb_lines==2:
            return 100
        elif nb_lines==3:
            return 300
        elif nb_lines==4:
            return 1200
        elif nb_lines>4:
            return 2000
        return 0

    def freeze_tetromino(self)->bool:
        ix = int((self.curTetromino.x+1)/CELL_SIZE)
        iy = int((self.curTetromino.y+1)/CELL_SIZE)
        for [vx,vy] in self.curTetromino.v:
            x = vx + ix
            y = vy + iy
            if (x>=0) and (x<NB_COLUMNS) and (y>=0) and (y<NB_ROWS) :
                self.board[x+y*NB_COLUMNS] = self.curTetromino.pieceShape

        self.nbCompletedLines = self.computeCompletedLines()
        if self.nbCompletedLines>0:
            self.score += self.compute_score(self.nbCompletedLines)
            self.score_label.text = 'SCORE : {:06d}'.format(self.score)
            return True

        return False

    def computeCompletedLines(self)->int :
        nbL = 0
        for y in range(0,NB_ROWS):
            #-- Check completed line
            f_complete = True
            for x in range(0,NB_COLUMNS):
                if self.board[x + y * NB_COLUMNS] == 0 :
                    f_complete = False
                    break
            if f_complete :
                nbL += 1
        return nbL

    def eraseFirstCompletedLine(self):
        for y in range(0,NB_ROWS):
            #-- Check completed line
            f_complete = True
            for x in range(0,NB_COLUMNS):
                if self.board[x + y * NB_COLUMNS] == 0 :
                    f_complete = False
                    break
            if f_complete :
                #-- Shift down the game board
                y1 = y
                while y1 < (NB_ROWS-1) :
                    ySrcOffset = (y1 + 1) * NB_COLUMNS
                    yDesOffset = y1 * NB_COLUMNS
                    for x in range(0,NB_COLUMNS) :
                        self.board[x + yDesOffset] = self.board[x + ySrcOffset]
                    y1 += 1
                return

    def tetrisRandomizer(self)->int:
        iSrc = 0
        ityp = 0
        if self.idTetroBag<14:
            ityp = self.tetroBag[self.idTetroBag]
            self.idTetroBag += 1
        else:
            # Shuttle Bag
            for _ in range(14):
                iSrc = randint(0, 13)
                ityp = self.tetroBag[iSrc]
                self.tetroBag[iSrc] = self.tetroBag[0]
                self.tetroBag[0] = ityp
            ityp = self.tetroBag[0]
            self.idTetroBag = 1
        return ityp

    def initNewGame(self):
        self.score = 0
        self.board = [0 for i in range(0,NB_COLUMNS*NB_ROWS)]
        self.nbCompletedLines = 0
        self.fDropTetromino = False
        self.fGameOver = False
        self.hVelocity = 0
        self.elapseTime1 = 0
        self.elapseTime2 = 0
        self.elapseTime3 = 0
        self.curTetromino = Tetromino(5*CELL_SIZE,18*CELL_SIZE,self.nextTetromino.pieceShape)
        self.nextTetromino = Tetromino(14*CELL_SIZE,10*CELL_SIZE,self.tetrisRandomizer())

    def draw_stanby(self):
        line1_label = pyglet.text.Label('TETRIS in PyGlet',font_name='sansation',
                                             font_size=14,bold=True,x=OX+NB_COLUMNS*CELL_SIZE/2,y=OY+16*CELL_SIZE,
                                             anchor_x='center',color=(255, 255, 0,255))
        line2_label = pyglet.text.Label('Press Space to Play',font_name='sansation',
                                             font_size=12,bold=True,x=OX+NB_COLUMNS*CELL_SIZE/2,y=OY+14*CELL_SIZE,
                                             anchor_x='center',color=(255, 255, 0,255))
        line1_label.draw()
        line2_label.draw()

    def draw_game_over(self):
        line1_label = pyglet.text.Label('Game Over',font_name='sansation',
                                             font_size=14,bold=True,x=OX+NB_COLUMNS*CELL_SIZE/2,y=OY+16*CELL_SIZE,
                                             anchor_x='center',color=(255, 255, 0,255))
        line2_label = pyglet.text.Label('Press Space to Continue',font_name='sansation',
                                             font_size=12,bold=True,x=OX+NB_COLUMNS*CELL_SIZE/2,y=OY+14*CELL_SIZE,
                                             anchor_x='center',color=(255, 255, 0,255))
        line1_label.draw()
        line2_label.draw()

    def draw_high_scrores(self):

        title_label = pyglet.text.Label('HIGH SCORES',font_name='sansation',
                                             font_size=14,bold=True,x=OX+NB_COLUMNS*CELL_SIZE/2,y=OY+18*CELL_SIZE,
                                             anchor_x='center',color=(255, 255, 0,255))

        yTop = y=OY+16*CELL_SIZE
        listHighScoresNames = [pyglet.text.Label('xxxxxx',font_name='sansation',
                                             font_size=12,bold=True,x=OX+CELL_SIZE,y=(yTop-i*CELL_SIZE),
                                             anchor_x='left',color=(255, 255, 0,255)) for i in range(10)]
        listHighScoresValues = [pyglet.text.Label('000000',font_name='sansation',
                                             font_size=12,bold=True,x=OX+NB_COLUMNS*CELL_SIZE/2,y=(yTop-i*CELL_SIZE),
                                             anchor_x='left',color=(255, 255, 0,255)) for i in range(10)]
        for i in range(10):
            hs = self.hightScores[i]
            lblName = listHighScoresNames[i]
            lblName.text = hs.name
            lblValue = listHighScoresValues[i]
            lblValue.text = '{:06d}'.format(hs.score)
            if i==self.idHightScore:
                if (self.iColorHighScore % 2)==0:
                    lblValue.color = (255, 255, 0,255)
                else:
                    lblValue.color = (55, 55, 0, 255)
                lblName.color = lblValue.color
            lblName.draw()
            lblValue.draw()

        title_label.draw()

    def on_draw(self):
        pyglet.gl.glClearColor(0.0,0.0,0.5,1.0)
        self.clear()
        self.boardRect.draw()

        # Clear Board
        rect = Rectangle(100,100,CELL_SIZE-2,CELL_SIZE-2,color=(0x00,0x00,0x00,0x00))
        
        self.score_label.draw()

        match self.mode:
            case GameMode.StandBy:
                self.draw_stanby()
            case GameMode.GameOver:
                self.draw_game_over()
            case GameMode.HightScore:
                self.draw_high_scrores()
            case GameMode.Play:
                # Draw Freeze Tetromino
                for y in range(0,NB_ROWS):
                    for x in range(0,NB_COLUMNS):
                        typ = self.board[x + y * NB_COLUMNS]
                        if typ != 0 :
                            rect.x = (x * (CELL_SIZE) + OX + 1)
                            rect.y = (y * (CELL_SIZE) + OY + 1)
                            rect.color = Tetromino.colorsTable[typ]
                            rect.draw()
                self.curTetromino.draw()

        self.nextTetromino.draw()


    def on_key_press(self,symbol, modifiers):

        match self.mode:
            case GameMode.Play:
                match symbol:
                    case key.LEFT:
                        self.hVelocity = -1
                    case key.RIGHT:
                        self.hVelocity = 1
                    case key.UP:
                        self.curTetromino.rotateRight()
                        savX = self.curTetromino.x
                        fUndo = False
                        if self.curTetromino.hitGround(self.board):
                            fUndo = True
                        elif self.curTetromino.isOutRightLimit():
                            # Try to shift inside board
                            while True:
                                self.curTetromino.x -= CELL_SIZE
                                if not self.curTetromino.isOutRightLimit():
                                    break
                            if self.curTetromino.hitGround(self.board):
                                fUndo = True
                        elif self.curTetromino.isOutLeftLimit():
                            # Try to shift inside board
                            while True:
                                self.curTetromino.x += CELL_SIZE
                                if not self.curTetromino.isOutLeftLimit():
                                    break
                            if self.curTetromino.hitGround(self.board):
                                fUndo = True
                        if fUndo:
                            self.curTetromino.x = savX
                            self.curTetromino.rotateLeft()
                    case key.ESCAPE:
                        Id = self.isHightScore()
                        if Id>=0:
                            self.insertHightScore(Id,self.player_name,self.score)
                            self.saveHightScore()
                            self.mode = GameMode.HightScore
                        else:
                            self.mode = GameMode.StandBy
                    case key.NUM_ADD | key.PAGEUP:
                        if self.musicVolume<10:
                            self.musicVolume += 1
                            self.myplayer.volume = self.musicVolume/10
                    case key.NUM_SUBTRACT | key.PAGEDOWN:
                        if self.musicVolume>0:
                            self.musicVolume -= 1
                            self.myplayer.volume = self.musicVolume/10

            case GameMode.StandBy:
                match symbol:
                    case key.NUM_ADD | key.PAGEUP:
                        if self.musicVolume<10:
                            self.musicVolume += 1
                            self.myplayer.volume = self.musicVolume/10
                    case key.NUM_SUBTRACT | key.PAGEDOWN:
                        if self.musicVolume>0:
                            self.musicVolume -= 1
                            self.myplayer.volume = self.musicVolume/10
                    case key.ESCAPE:
                        pyglet.app.exit()

            case GameMode.HightScore:
                match symbol:
                    case key.NUM_ADD | key.PAGEUP:
                        if self.musicVolume<10:
                            self.musicVolume += 1
                            self.myplayer.volume = self.musicVolume/10
                    case key.NUM_SUBTRACT | key.PAGEDOWN:
                        if self.musicVolume>0:
                            self.musicVolume -= 1
                            self.myplayer.volume = self.musicVolume/10
                    case key.ESCAPE:
                        if self.idHightScore>=-1:
                            if len(self.player_name)==0:
                                self.player_name = "XXXXXXXX"
                            self.setHightScoreName(self.player_name)
                            self.saveHightScore()
                        self.mode = GameMode.StandBy
                    case key.BACKSPACE:
                        if len(self.player_name)>0:
                            self.player_name = self.player_name[:-1]
                            self.setHightScoreName(self.player_name)                
                    case key.RETURN:
                        if self.idHightScore>=-1:
                            if len(self.player_name)==0:
                                self.player_name = "XXXXXXXX"
                            self.setHightScoreName(self.player_name)
                            self.saveHightScore()
                        self.mode = GameMode.StandBy
                    case _:
                        c = self.tblChars.get(symbol)
                        if c!=None:
                            self.player_name = self.player_name + c
                            self.setHightScoreName(self.player_name) 

    def on_key_release(self,symbol, modifiers):
        match symbol:
            case key.LEFT:
                self.hVelocity = 0
            case key.RIGHT:
                self.hVelocity = 0
            case key.SPACE:
                match self.mode:
                    case GameMode.Play:
                        self.fDropTetromino = True
                    case GameMode.StandBy:
                        self.mode = GameMode.Play
                        self.initNewGame()
                    case GameMode.GameOver:
                        self.mode = GameMode.StandBy

            case key.M:
                if self.myplayer.playing:
                    self.myplayer.pause()
                else:
                    self.myplayer.play()
            case _:
                pass


    def on_update(self,deltatime):

        self.elapseTime1 += deltatime
        self.elapseTime2 += deltatime
        self.elapseTime3 += deltatime
        match self.mode:
            case GameMode.Play:
                if self.nbCompletedLines>0:
                    if self.elapseTime1 > 0.2:
                        self.elapseTime1 = 0
                        self.eraseFirstCompletedLine()
                        self.nbCompletedLines -= 1
                        self.soundSucces.play()
                    return
                
                if self.fGameOver:
                    if self.elapseTime1 > 0.4:
                        id = self.isHightScore()
                        if id>=0:
                            self.insertHightScore(id,self.player_name,self.score)
                            self.saveHightScore()
                            self.mode = GameMode.HightScore
                        else:
                            self.mode = GameMode.GameOver
                    return

                # Horizontal move
                if self.elapseTime1 > 0.03:
                    self.elapseTime1 = 0
                    for _ in range(4):
                        if self.curTetromino.velocityX == 1:
                            dum = self.curTetromino.x + self.curTetromino.velocityX
                            if (dum % CELL_SIZE)!=0:
                                if not (self.curTetromino.hitRight(self.board)):
                                    self.curTetromino.x += self.curTetromino.velocityX                    
                            else:
                                self.curTetromino.x += self.curTetromino.velocityX
                                self.curTetromino.velocityX = 0
                        elif self.curTetromino.velocityX == -1:
                            dum = self.curTetromino.x + self.curTetromino.velocityX
                            if (dum % CELL_SIZE)!=0:
                                if not (self.curTetromino.hitLeft(self.board)):
                                    self.curTetromino.x += self.curTetromino.velocityX                    
                            else:
                                self.curTetromino.x += self.curTetromino.velocityX
                                self.curTetromino.velocityX = 0
                        else:            
                            if  self.hVelocity==-1:
                                if (self.curTetromino.x % CELL_SIZE)==0:
                                    _x = self.curTetromino.minX() + self.curTetromino.iX()
                                    if  _x > 0:
                                        self.curTetromino.velocityX = -1
                                        if not (self.curTetromino.hitLeft(self.board)):
                                            self.curTetromino.x += self.curTetromino.velocityX

                            elif self.hVelocity==1:
                                if (self.curTetromino.x % CELL_SIZE)==0:
                                    _x = self.curTetromino.maxX() + self.curTetromino.iX()
                                    if _x<(NB_COLUMNS-1):
                                        self.curTetromino.velocityX = 1
                                        if not (self.curTetromino.hitRight(self.board)):
                                            self.curTetromino.x += self.curTetromino.velocityX

                # Move Down
                if self.fDropTetromino:
                    delay = 0.01
                    nbRepeat = 10
                else:
                    delay = 0.03
                    nbRepeat = 3

                if self.elapseTime3 > delay:
                    self.elapseTime3 = 0
                    for _ in range(nbRepeat):
                        # Test hit freeze tetromino's cells
                        fHit = False
                        for [vx,vy] in self.curTetromino.v:
                            x = vx*CELL_SIZE + self.curTetromino.x
                            y = vy*CELL_SIZE + self.curTetromino.y - 1
                            ix = int(x/CELL_SIZE)
                            iy = int(y/CELL_SIZE)
                            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                                if self.board[ix+iy*NB_COLUMNS]!=0:
                                    fHit = True
                                    break
                            x = vx*CELL_SIZE + self.curTetromino.x + CELL_SIZE - 1
                            ix = int(x/CELL_SIZE)
                            if (ix>=0) and (ix<NB_COLUMNS) and (iy>=0) and (iy<NB_ROWS):
                                if self.board[ix+iy*NB_COLUMNS]!=0:
                                    fHit = True
                                    break
                        if (fHit):
                            if (self.curTetromino.x % CELL_SIZE)==0 and (self.curTetromino.y % CELL_SIZE)==0:
                                self.freeze_tetromino()
                                if self.is_game_over():
                                    self.fGameOver = True
                                else:
                                    self.fDropTetromino = False
                                    self.curTetromino = Tetromino(5*CELL_SIZE,19*CELL_SIZE,self.nextTetromino.pieceShape)
                                    self.nextTetromino = Tetromino(14*CELL_SIZE,11*CELL_SIZE,self.tetrisRandomizer())
                        else:
                            # Current Tetromino reach the bottom
                            if not self.curTetromino.hitBottom():
                                self.curTetromino.y += self.curTetromino.velocityY
                                if (self.curTetromino.x%CELL_SIZE)==0:
                                    if (self.curTetromino.y%CELL_SIZE)==0:
                                        # Allow horizontal sliding
                                        if  self.hVelocity!=0:
                                            break
                            else:
                                if self.hVelocity!=0:
                                    # Allow horizontal movement
                                    break
                                else:
                                    # Freeze current Tetromino
                                    # Ajust Tetromino horizontal position
                                    if self.curTetromino.x%CELL_SIZE!=0:
                                        self.curTetromino.x = (int(self.curTetromino.x/CELL_SIZE)+1)*CELL_SIZE
                                    # Freeze
                                    self.freeze_tetromino()
                                    if self.is_game_over():
                                        self.fGameOver = True
                                    else:
                                        self.fDropTetromino = False
                                        self.curTetromino = Tetromino(5*CELL_SIZE,19*CELL_SIZE,self.nextTetromino.pieceShape)
                                        self.nextTetromino = Tetromino(14*CELL_SIZE,11*CELL_SIZE,self.tetrisRandomizer())
            case GameMode.HightScore:
                if self.elapseTime1 > 0.2:
                    self.elapseTime1 = 0
                    self.iColorHighScore += 1

        if self.elapseTime2 > 0.5:
            self.elapseTime2 = 0
            self.nextTetromino.rotateLeft()


if __name__ == "__main__" :
    fenetre = Fenetre(WIN_WIDTH,WIN_HEIGHT)
    clock.schedule_interval(fenetre.on_update,1/100)
    pyglet.app.run()
