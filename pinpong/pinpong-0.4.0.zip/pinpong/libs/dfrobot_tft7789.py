# -*- coding: utf-8 -*-
import time
import freetype
from PIL import Image, ImageSequence
from pinpong.board import gboard,SPI

class TFT7789:
  initCmd = [
    #flag cmd 最高位为1表示后2位是延时，低7位表示参数的个数
    0x01, 0x01, 0x80, 0, 150,
    0x01, 0x11, 0x80, 0, 120,
    0x01, 0x3A, 1, 0x55,
    0x01, 0x36, 1, 0x00,
    0x01, 0x21, 0,
    0x01, 0x13, 0,
    0x01, 0x29, 0,
    0x00
  ]
  
  _TFT7789_COLSET = 0x2A
  _TFT7789_RAWSET = 0x2B
  _TFT7789_RAMWR  = 0x2C

  
  COLOR_BLACK  = 0x0000   #  黑色    
  COLOR_BLUE   = 0x001F   #  深蓝色  
  COLOR_GREEN  = 0x07E0   #  深绿色 
  COLOR_RED    = 0xF800   #  深红色
  COLOR_WHITE  = 0xffff   #  白色 
  
  def __init__(self, width, height):
    self.width = width
    self.height = height

  def begin(self):
    offset = 0
    while self.initCmd[offset]:
      offset += 1
      cmd = self.initCmd[offset]
      offset += 1
      val = self.initCmd[offset]
      offset += 1
      argsNum = val & 0x7F
      if val & 0x80:
        duration = self.initCmd[offset]*255 + self.initCmd[offset+1]
        time.sleep(duration/1000)
        offset += 2
      self.sendCommand(cmd, self.initCmd[offset:offset+argsNum])
      offset += argsNum
    
  def show(self,buf,x1,y1,x2,y2):
    self.sendCommand(self._TFT7789_COLSET)
    self.sendData16(x1)#x起始坐标
    self.sendData16(x2)#x结束坐标
    self.sendCommand(self._TFT7789_RAWSET)
    self.sendData16(y1)#y起始坐标
    self.sendData16(y2)#y结束坐标
    self.sendCommand(self._TFT7789_RAMWR)
    self.sendBuf(buf)
    


class TFT7789_SPI(TFT7789):
  def __init__(self, board=None, width=240, height=240, bus_num=1, device_num=0, dc=None, res=None, cs=None):
    if board is None:
      board = gboard

    self.board = board
    self.dc=dc
    self.cs=cs
    self.res=res
    self.spi = SPI(bus_num=bus_num,device_num=device_num)
    self._ft = FRAME_BUF('msyh.ttf')
    super().__init__(width, height)

  def begin(self):
    if self.res:
      self.res.value(1)
    if self.dc:
      self.dc.value(1)

    if self.res:
      self.res.value(0)
      time.sleep(0.2)
      self.res.value(1)
      time.sleep(0.2)
    super().begin()

  def sendCommand(self, cmd, value=None):
    self.dc.value(0)
    self.spi.write([cmd])
    self.dc.value(1)
    if value:
      self.spi.write(value)

  def sendData16(self, data):
    self.spi.write([data>>8, data&0xff])
  
  def sendColor(self, color, len):
    buf = [color>>8, color&0xff]*len
    self.spi.write(buf)

  def sendBuf(self,buf):
    self.spi.write(buf)

#委托模式，方法在FRAME_BUF类中实现
  def fill(self,color):
    return self._ft.lcd_fill(color,self)

  def text(self,color,x,y,text,text_size):
    return self._ft.lcd_draw_text(color,x,y,text,text_size,self)
    
  def rectangle(self,color,x1,y1,x2,y2,flag):
    return self._ft.lcd_draw_rectangle(color,x1,y1,x2,y2,flag,self)
  
  def circle(self,color,x,y,r):
    return self._ft.lcd_draw_circle(color,x,y,r,self)
  
  def line(self,color,x1,y1,x2,y2):
    return self._ft.lcd_draw_line(color,x1,y1,x2,y2,self)
  
  def picture(self,filename,x,y,size):
    return self._ft.lcd_draw_picture(filename,x,y,size,self)

class FRAME_BUF(object):

 send_pixel = []
 pixel = [[0 for col in range(2)] for row in range(240*240)]#定义一个二维列表

 def __init__(self, str):
  self._face = freetype.Face(str)

 def lcd_draw_text(self, text_color, x, y, text, text_size, obj):
  '''
  draw chinese(or not) text with ttf
  :param image:  image(numpy.ndarray) to draw text
  :param pos:  where to draw text
  :param text:  the context, for chinese should be unicode type
  :param text_size: text size
  :param text_color:text color
  :return:   image
  '''
  self._face.set_char_size(text_size * 64)
  metrics = self._face.size
  ascender = metrics.ascender / 64.0
  ypos = int(ascender)
  text = text
  self.draw_string(x, y + ypos, text, text_color)
  self.lcd_show(obj,x, y, text_size*len(text), text_size)


 def draw_string(self, x_pos, y_pos, text, color):
  '''
  draw string
  :param x_pos: text x-postion on img
  :param y_pos: text y-postion on img
  :param text: text (unicode)
  :param color: text color
  :return:  image
  '''
  prev_char = 0
  pen = freetype.Vector()
  pen.x = x_pos << 6 # div 64
  pen.y = y_pos << 6
  hscale = 1.0
  matrix = freetype.Matrix(int(hscale) * 0x10000, int(0.2 * 0x10000), \
         int(0.0 * 0x10000), int(1.1 * 0x10000))
  cur_pen = freetype.Vector()
  pen_translate = freetype.Vector()
  x = 0
  y = 0
  for cur_char in text:
   self._face.set_transform(matrix, pen_translate)
   self._face.load_char(cur_char)
   kerning = self._face.get_kerning(prev_char, cur_char)
   pen.x += kerning.x
   slot = self._face.glyph
   bitmap = slot.bitmap
   cur_pen.x = pen.x
   cur_pen.y = pen.y - slot.bitmap_top * 64
   self.draw_ft_bitmap(bitmap, cur_pen, color,x,y)
   x = x + 30
   pen.x += slot.advance.x
   prev_char = cur_char


 #freetype显示
 def draw_ft_bitmap(self, bitmap, pen, color, x, y):
  '''
  draw each char
  :param bitmap: bitmap
  :param pen: pen
  :param color: pen color e.g.(0,0,255) - red
  :return:  image
  '''
  x_pos = pen.x >> 6
  y_pos = pen.y >> 6
  cols = bitmap.width
  rows = bitmap.rows
  glyph_pixels = bitmap.buffer
  temp = x
  for row in range(rows):
   for col in range(cols):
    if glyph_pixels[row * cols + col] != 0:
     self.pixel[y*240+x] = [(color|self.pixel[y*240+x][1])>>8,color|self.pixel[y*240+x][1]]#将像素点的颜色数据填充进二维列表里面
     x = x + 1
    else:
     #该像素点没数据，跳过    
     x = x + 1
   #换行
   y = y + 1
   x = temp#x轴方向的起始坐标


 def lcd_draw_line(self,color,x1,y1,x2,y2,obj):
   delta_x = x2 - x1
   delta_y = y2 - y1
   if delta_x > 0:
     incx = 1
   elif delta_x == 0:
     incx = 0 
   else:
     incx = -1
     delta_x = -delta_x
   if delta_y > 0:
     incy = 1
   elif delta_y == 0:
     incy = 0
   else:
     incy = -1
     delta_y = -delta_y
   if delta_x > delta_y:
     distance = delta_x
   else:
     distance = delta_y
   x = x1
   y = y1
   x_temp = 0
   y_temp = 0
   for i in range(0,distance+2):
     self.pixel[y*240+x] = [(color|self.pixel[y*240+x][1])>>8,color|(self.pixel[y*240+x][1])]#填充像素点信息
     x_temp += delta_x
     if x_temp > distance:
       x_temp -= distance
       x += incx
     y_temp += delta_y
     if y_temp > distance:
       y_temp -= distance
       y += incy
   self.lcd_show(obj,x1,y1,x2,y2)    

 def lcd_draw_rectangle(self,color,x1,y1,x2,y2,flag,obj):
   if flag == 1:#空心矩形
     self.lcd_draw_line(color, x1, y1, x2, y1,obj)
     self.lcd_draw_line(color, x1, y1, x1, y2,obj)
     self.lcd_draw_line(color, x1, y2, x2, y2,obj)
     self.lcd_draw_line(color, x2, y1, x2, y2,obj)
   else:#实心矩形
     for x in range(x1,x2):
       for y in range(y1,y2):
         self.pixel[y*240+x] = [(color|self.pixel[y*240+x][1])>>8,color|self.pixel[y*240+x][1]]#两个for循环 填充实心矩形
   self.lcd_show(obj,x1,y1,x2,y2)

 def lcd_draw_circle(self,color,x,y,r,obj):#画圆
   a = 0
   b = r
   d = 3 - (r << 1)
   while (a <= b):
     #填充像素点信息
     self.pixel[(y-a)*240+(x-b)] = [(color|self.pixel[(y-a)*240+(x-b)][1])>>8,color|self.pixel[(y-a)*240+(x-b)][1]]#这是二维列表
     self.pixel[(y-a)*240+(x+b)] = [(color|self.pixel[(y-a)*240+(x+b)][1])>>8,color|self.pixel[(y-a)*240+(x+b)][1]]#这是二维列表
     self.pixel[(y+b)*240+(x-a)] = [(color|self.pixel[(y+b)*240+(x-a)][1])>>8,color|self.pixel[(y+b)*240+(x-a)][1]]#这是二维列表
     self.pixel[(y-a)*240+(x-b)] = [(color|self.pixel[(y-a)*240+(x-b)][1])>>8,color|self.pixel[(y-a)*240+(x-b)][1]]#这是二维列表
     self.pixel[(y-b)*240+(x-a)] = [(color|self.pixel[(y-b)*240+(x-a)][1])>>8,color|self.pixel[(y-b)*240+(x-a)][1]]#这是二维列表
     self.pixel[(y+a)*240+(x+b)] = [(color|self.pixel[(y+a)*240+(x+b)][1])>>8,color|self.pixel[(y+a)*240+(x+b)][1]]#这是二维列表
     self.pixel[(y-b)*240+(x+a)] = [(color|self.pixel[(y-b)*240+(x+a)][1])>>8,color|self.pixel[(y-b)*240+(x+a)][1]]#这是二维列表
     self.pixel[(y+b)*240+(x+a)] = [(color|self.pixel[(y+b)*240+(x+a)][1])>>8,color|self.pixel[(y+b)*240+(x+a)][1]]#这是二维列表
     self.pixel[(y+a)*240+(x-b)] = [(color|self.pixel[(y+a)*240+(x-b)][1])>>8,color|self.pixel[(y+a)*240+(x-b)][1]]#这是二维列表
     a = a + 1
     if d < 0:
       d += 4 * a + 6
     else:
       d += 10 + 4 * (a - b)
       b = b - 1
     self.pixel[(y+b)*240+(x+a)] = [(color|self.pixel[(y+b)*240+(x+a)][1])>>8,color|self.pixel[(y+b)*240+(x+a)][1]]#这是二维列表
   self.lcd_show(obj,x-r,y-r,x+r,y+r)

 def lcd_draw_picture(self,filename,x,y,size,obj):
   img = Image.open(filename)
   if((filename[-3:-1:]+filename[-1]) == "gif" or (filename[-3:-1:]+filename[-1]) == "GIF"):
     for frame in ImageSequence.all_frames(img):
      frame = frame.convert("RGB")
      frame.thumbnail((size,size))
      for i in range(0,frame.size[1]):
        for m in range(0,frame.size[0]):
          R = frame.getpixel((m,i))[0] >> 3
          G = frame.getpixel((m,i))[1] >> 2
          B = frame.getpixel((m,i))[2] >> 3
          color = (R << 11)|(G << 5)|(B)
          self.pixel[(y+i)*240+(x+m)] = [color>>8,color]
      self.lcd_show(obj,x,y,(x+size),(y+size))
   else:
     img = img.convert("RGB")
     img.thumbnail((size,size))
     for i in range(0,img.size[1]):
        for m in range(0,img.size[0]):
          R = img.getpixel((m,i))[0] >> 3
          G = img.getpixel((m,i))[1] >> 2
          B = img.getpixel((m,i))[2] >> 3
          color = (R << 11)|(G << 5)|(B)
          self.pixel[(y+i)*240+(x+m)] = [color>>8,color]
     self.lcd_show(obj,x,y,(x+size),(y+size))
 
 def lcd_fill(self,color,obj):
    for i in range(obj.width*obj.height):
      self.pixel[i] = [color>>8,color]
    self.lcd_show(obj,0,0,obj.width,obj.height)  

 def lcd_show(self,obj,x1,y1,x2,y2):
   buf=[]
   length_x =  abs(x1-x2) + 1
   length_y =  abs(y1-y2) + 1
   for y in range(0,length_y):
    buf += [n for a in self.pixel[((y1+y)*240+x1):((y1+y)*240+x1+length_x)] for n in a ]#展开成一维列表
   obj.show(buf,x1,y1,x2,y2)

