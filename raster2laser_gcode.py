#!/usr/bin/python3
#pylint: disable = wrong-import-position, wrong-import-order, no-name-in-module, no-self-use, too-many-statements, too-many-nested-blocks, line-too-long, too-many-locals, invalid-name, missing-docstring, too-many-return-statements, inconsistent-return-statements, bad-continuation, too-many-branches
'''
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
#
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own:P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
'''
import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions')

import subprocess

import inkex
import png

# import ptvsd
# ptvsd.enable_attach(address=('localhost', 5678))
# ptvsd.wait_for_attach()


class GcodeExport(inkex.Effect):

    ######## 	Richiamata da _main()
    def __init__(self):
        """init the effetc library and get options from gui"""
        inkex.Effect.__init__(self)

        # Opzioni di esportazione dell'immagine
        self.arg_parser.add_argument("-d", "--directory", type=str, dest="directory", default="/home/", help="Directory for files") ####check_dir
        self.arg_parser.add_argument("-file", "--filename", type=str, dest="filename", default="-1.0", help="File name")
        self.arg_parser.add_argument("-extension", "--extension", type=str, dest="extension", default="ngc", help="File name extension")
        self.arg_parser.add_argument("-n", "--add-numeric-suffix-to-filename", type=inkex.utils.Boolean, dest="add_numeric_suffix_to_filename", default=True, help="Add numeric suffix to filename")
        self.arg_parser.add_argument("-r", "--resolution", type=int, dest="resolution", default="5", help="") #Usare il valore su float(xy)/resolution e un case per i DPI dell export

        # Come convertire in scala di grigi
        self.arg_parser.add_argument("-g", "--grayscale_type", type=int, dest="grayscale_type", default="1", help="")

        # Modalita di conversione in Bianco e Nero
        self.arg_parser.add_argument("-c", "--conversion_type", type=int, dest="conversion_type", default="1", help="")

        # Opzioni modalita
        self.arg_parser.add_argument("-BW", "--BW_threshold", type=int, dest="BW_threshold", default="128", help="")
        self.arg_parser.add_argument("-GS", "--grayscale_resolution", type=int, dest="grayscale_resolution", default="1", help="")

        #Velocita Nero e spostamento
        self.arg_parser.add_argument("-s", "--feed", type=int, dest="feed", default="200", help="")
        self.arg_parser.add_argument("-p", "--power", type=int, dest="power", default="80", help="")

        # Mirror Y
        self.arg_parser.add_argument("-f", "--flip_y", type=inkex.utils.Boolean, dest="flip_y", default=False, help="")

        # Homing
        self.arg_parser.add_argument("-home", "--homing", type=int, dest="homing", default="1", help="")

        # Laser ON/OFF commands
        self.arg_parser.add_argument("-lon", "--laseron", type=str, dest="laseron", default="M03", help="")
        self.arg_parser.add_argument("-loff", "--laseroff", type=str, dest="laseroff", default="M05", help="")
        self.arg_parser.add_argument("-mp", "--laser_max_value", type=int, dest="laser_max_value", default="255", help="")
        self.arg_parser.add_argument("-lminsw", "--laserminsw", type=inkex.utils.Boolean, dest="laserminsw", default=True, help="Minimize Laser switching")

        #inkex.errormsg("BLA BLA BLA Messaggio da visualizzare") #DEBUG

    ######## 	Richiamata da __init__()
    ########	Qui si svolge tutto
    def effect(self):

        ##Implementare check_dir
        if os.path.isdir(self.options.directory):

            #Aggiungo un suffisso al nomefile per non sovrascrivere dei file
            if self.options.add_numeric_suffix_to_filename:
                dir_list = os.listdir(self.options.directory) #List di tutti i file nella directory di lavoro
                temp_name = self.options.filename
                max_n = 0
                for s in dir_list:
                    r = re.match("^%s_0*(\d+).*%s$"%(re.escape(temp_name), '\\.png'), s)
                    if r:
                        max_n = max(max_n, int(r.group(1)))
                self.options.filename = temp_name + "_" + ("0"*(4-len(str(max_n+1))) + str(max_n+1))

            #genero i percorsi file da usare
            suffix = ""
            if self.options.conversion_type == 1:
                suffix = "_BWfix_"+str(self.options.BW_threshold)+"_"
            elif self.options.conversion_type == 2:
                suffix = "_BWrnd_"
            elif self.options.conversion_type == 3:
                suffix = "_H_"
            elif self.options.conversion_type == 4:
                suffix = "_Hrow_"
            elif self.options.conversion_type == 5:
                suffix = "_Hcol_"
            else:
                if self.options.grayscale_resolution == 1:
                    suffix = "_Gray_256_"
                elif self.options.grayscale_resolution == 2:
                    suffix = "_Gray_128_"
                elif self.options.grayscale_resolution == 4:
                    suffix = "_Gray_64_"
                elif self.options.grayscale_resolution == 8:
                    suffix = "_Gray_32_"
                elif self.options.grayscale_resolution == 16:
                    suffix = "_Gray_16_"
                elif self.options.grayscale_resolution == 32:
                    suffix = "_Gray_8_"
                else:
                    suffix = "_Gray_"

            pos_file_png_original = os.path.join(self.options.directory, self.options.filename+suffix+"-orignal.png")
            pos_file_png_BW = os.path.join(self.options.directory, self.options.filename+suffix+"preview-BW.png")
            pos_file_png_GS = os.path.join(self.options.directory, self.options.filename+suffix+"preview-GS.png")
            pos_file_gcode = os.path.join(self.options.directory, self.options.filename+suffix+"final." + self.options.extension)


            #Esporto l'immagine in PNG
            self.exportPage(pos_file_png_original)


            #DA FARE
            #Manipolo l'immagine PNG per generare il file Gcode
            self.PNGtoGcode(pos_file_png_original, pos_file_png_BW, pos_file_png_GS, pos_file_gcode)


        else:
            inkex.errormsg("Directory does not exist! Please specify existing directory!")


    ########	ESPORTA L IMMAGINE IN PNG
    ######### 	Richiamata da effect()
    def exportPage(self, pos_file_png_original):
        ######## CREAZIONE DEL FILE PNG ########
        #Crea l'immagine dentro la cartella indicata  da "pos_file_png_original"
        # -d 127 = risoluzione 127DPI  =>  5 pixel/mm  1pixel = 0.2mm
        ###command="inkscape -C -e \"%s\" -b\"%s\" %s -d 127" % (pos_file_png_original)

        if self.options.resolution == 1:
            DPI = 25
        elif self.options.resolution == 2:
            DPI = 50
        elif self.options.resolution == 5:
            DPI = 127
        else:
            DPI = 254

        command = "inkscape -C -o \"%s\" -d %s -y 1 %s" % (pos_file_png_original, DPI, self.options.input_file)  #Comando da linea di comando per esportare in PNG

        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        p.wait()
        p.stderr.close()





    ########	CREA IMMAGINE IN B/N E POI GENERA GCODE
    ######## 	Richiamata da effect()
    def PNGtoGcode(self, pos_file_png_original, pos_file_png_BW, pos_file_png_GS, pos_file_gcode):

        ######## GENERO IMMAGINE IN SCALA DI GRIGI ########
        #Scorro l immagine e la faccio diventare una matrice composta da list
        reader = png.Reader(pos_file_png_original)#File PNG generato
        w, h, pixels, metadata = reader.read_flat()
        matrice = [[0 for i in range(w)]for j in range(h)]  #List al posto di un array



        #Scrivo una nuova immagine in Scala di grigio 8bit
        #copia pixel per pixel
        if self.options.grayscale_type == 1:
            #0.21R + 0.71G + 0.07B
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    matrice[y][x] = int(pixels[pixel_position]*0.21 + pixels[(pixel_position+1)]*0.71 + pixels[(pixel_position+2)]*0.07)
        elif self.options.grayscale_type == 2:
            #(R+G+B)/3
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    matrice[y][x] = int((pixels[pixel_position] + pixels[(pixel_position+1)]+ pixels[(pixel_position+2)]) / 3)
        elif self.options.grayscale_type == 3:
            #R
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    matrice[y][x] = int(pixels[pixel_position])
        elif self.options.grayscale_type == 4:
            #G
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    matrice[y][x] = int(pixels[(pixel_position+1)])
        elif self.options.grayscale_type == 5:
            #B
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    matrice[y][x] = int(pixels[(pixel_position+2)])
        elif self.options.grayscale_type == 6:
            #Max Color
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    list_RGB = pixels[pixel_position], pixels[(pixel_position+1)], pixels[(pixel_position+2)]
                    matrice[y][x] = int(max(list_RGB))
        else:
            #Min Color
            for y in range(h): # y varia da 0 a h-1
                for x in range(w): # x varia da 0 a w-1
                    pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
                    list_RGB = pixels[pixel_position], pixels[(pixel_position+1)], pixels[(pixel_position+2)]
                    matrice[y][x] = int(min(list_RGB))
        ####Ora matrice contiene l'immagine in scala di grigi


        #### Saving Grayscale image ####
        file_img_GS = open(pos_file_png_GS, 'wb') #Creo il file
        Costruttore_img = png.Writer(w, h, greyscale=True, bitdepth=8) #Impostazione del file immagine
        Costruttore_img.write(file_img_GS, matrice) #Costruttore del file immagine
        file_img_GS.close()	#Chiudo il file




        ######## GENERO IMMAGINE IN BIANCO E NERO ########
        #Scorro matrice e genero matrice_BN
        B = 255
        N = 0
        matrice_BN = [[255 for i in range(w)]for j in range(h)]
        if self.options.conversion_type == 1:
            #B/W fixed threshold
            soglia = self.options.BW_threshold
            for y in range(h):
                for x in range(w):
                    if matrice[y][x] >= soglia:
                        matrice_BN[y][x] = B
                    else:
                        matrice_BN[y][x] = N
        elif self.options.conversion_type == 2:
            #B/W random threshold
            from random import randint
            for y in range(h):
                for x in range(w):
                    soglia = randint(20, 235)
                    if matrice[y][x] >= soglia:
                        matrice_BN[y][x] = B
                    else:
                        matrice_BN[y][x] = N
        elif self.options.conversion_type == 3:
            #Halftone
            Step1 = [[B, B, B, B, B], [B, B, B, B, B], [B, B, N, B, B], [B, B, B, B, B], [B, B, B, B, B]]
            Step2 = [[B, B, B, B, B], [B, B, N, B, B], [B, N, N, N, B], [B, B, N, B, B], [B, B, B, B, B]]
            Step3 = [[B, B, N, B, B], [B, N, N, N, B], [N, N, N, N, N], [B, N, N, N, B], [B, B, N, B, B]]
            Step4 = [[B, N, N, N, B], [N, N, N, N, N], [N, N, N, N, N], [N, N, N, N, N], [B, N, N, N, B]]

            for y in range(int(int(h)/5)):
                for x in range(int(int(w)/5)):
                    media = 0
                    for y2 in range(5):
                        for x2 in range(5):
                            media += matrice[y*5+y2][x*5+x2]
                    media = media /25
                    for y3 in range(5):
                        for x3 in range(5):
                            if media >= 250 and media <= 255:
                                matrice_BN[y*5+y3][x*5+x3] = B
                            if media >= 190 and media < 250:
                                matrice_BN[y*5+y3][x*5+x3] = Step1[y3][x3]
                            if media >= 130 and media < 190:
                                matrice_BN[y*5+y3][x*5+x3] = Step2[y3][x3]
                            if media >= 70 and media < 130:
                                matrice_BN[y*5+y3][x*5+x3] = Step3[y3][x3]
                            if media >= 10 and media < 70:
                                matrice_BN[y*5+y3][x*5+x3] = Step4[y3][x3]
                            if media >= 0 and media < 10:
                                matrice_BN[y*5+y3][x*5+x3] = N
        elif self.options.conversion_type == 4:
            #Halftone row
            Step1r = [B, B, N, B, B]
            Step2r = [B, N, N, B, B]
            Step3r = [B, N, N, N, B]
            Step4r = [N, N, N, N, B]

            for y in range(h):
                for x in range(w/5):
                    media = 0
                    for x2 in range(5):
                        media += matrice[y][x*5+x2]
                    media = media /5
                    for x3 in range(5):
                        if media >= 250 and media <= 255:
                            matrice_BN[y][x*5+x3] = B
                        if media >= 190 and media < 250:
                            matrice_BN[y][x*5+x3] =	Step1r[x3]
                        if media >= 130 and media < 190:
                            matrice_BN[y][x*5+x3] =	Step2r[x3]
                        if media >= 70 and media < 130:
                            matrice_BN[y][x*5+x3] =	Step3r[x3]
                        if media >= 10 and media < 70:
                            matrice_BN[y][x*5+x3] =	Step4r[x3]
                        if media >= 0 and media < 10:
                            matrice_BN[y][x*5+x3] = N
        elif self.options.conversion_type == 5:
            #Halftone column
            Step1c = [B, B, N, B, B]
            Step2c = [B, N, N, B, B]
            Step3c = [B, N, N, N, B]
            Step4c = [N, N, N, N, B]

            for y in range(h/5):
                for x in range(w):
                    media = 0
                    for y2 in range(5):
                        media += matrice[y*5+y2][x]
                    media = media /5
                    for y3 in range(5):
                        if media >= 250 and media <= 255:
                            matrice_BN[y*5+y3][x] = B
                        if media >= 190 and media < 250:
                            matrice_BN[y*5+y3][x] =	Step1c[y3]
                        if media >= 130 and media < 190:
                            matrice_BN[y*5+y3][x] =	Step2c[y3]
                        if media >= 70 and media < 130:
                            matrice_BN[y*5+y3][x] =	Step3c[y3]
                        if media >= 10 and media < 70:
                            matrice_BN[y*5+y3][x] =	Step4c[y3]
                        if media >= 0 and media < 10:
                            matrice_BN[y*5+y3][x] = N
        else:
            #Grayscale
            if self.options.grayscale_resolution == 1:
                matrice_BN = matrice
            else:
                for y in range(h):
                    for x in range(w):
                        if matrice[y][x] <= 1:
                            matrice_BN[y][x] = N
                        elif matrice[y][x] >= 254:
                            matrice_BN[y][x] = B
                        else:
                            matrice_BN[y][x] = (matrice[y][x] // self.options.grayscale_resolution) * self.options.grayscale_resolution
        ####Ora matrice_BN contiene l'immagine in Bianco (255) e Nero (0)


        #### SALVO IMMAGINE IN BIANCO E NERO ####
        file_img_BN = open(pos_file_png_BW, 'wb') #Creo il file
        Costruttore_img = png.Writer(w, h, greyscale=True, bitdepth=8) #Impostazione del file immagine
        Costruttore_img.write(file_img_BN, matrice_BN) #Costruttore del file immagine
        file_img_BN.close()	#Chiudo il file






        #### GENERO IL FILE GCODE ####
        if not self.options.flip_y: #Inverto asse Y solo se flip_y = False
            #-> coordinate Cartesiane (False) Coordinate "informatiche" (True)
            matrice_BN.reverse()

        Laser_ON = False
        Feed = self.options.feed
        LaserMaxValue = self.options.laser_max_value
        Power = self.options.power * LaserMaxValue/100
        Scala = self.options.resolution
        file_gcode = open(pos_file_gcode, 'w')  #Creo il file

        #Configurazioni iniziali standard Gcode
        file_gcode.write('; Generated with:\n; "Raster 2 Laser Gcode generator"\n; by 305 Engineering\n;\n; Inkscape 1.x mod by +BFerrarese\n;\n')
        #HOMING
        if self.options.homing == 1:
            file_gcode.write('G28; home all axes\n')
        elif self.options.homing == 2:
            file_gcode.write('$H; home all axes\n')
        else:
            pass
        file_gcode.write('G21; Set units to millimeters\n')
        file_gcode.write('G90; Use absolute coordinates\n')
        if self.options.laserminsw:
            file_gcode.write(self.options.laseron + ' ; LASER ON\n\n\n')
        else:
            file_gcode.write(self.options.laseroff + ' ; LASER OFF\n\n\n')


        file_gcode.write('G0' +' F' + str(Feed) + '\n')
        file_gcode.write('G1' +' F' + str(Feed) + ' S' + str(Power) + '\n\n')

        #Creazione del Gcode

        #allargo la matrice per lavorare su tutta l'immagine
        for y in range(h):
            matrice_BN[y].append(B)
        w = w+1

        if self.options.conversion_type != 6:
            for y in range(h):
                if y % 2 == 0:
                    for x in range(w):
                        if matrice_BN[y][x] == N:
                            if not Laser_ON:
                                file_gcode.write('G0 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
                                if not self.options.laserminsw:
                                    file_gcode.write(self.options.laseron + '\n')
                                Laser_ON = True
                            if  Laser_ON:   #DEVO evitare di uscire dalla matrice
                                if x == w-1:
                                    file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n')
                                    if not self.options.laserminsw:
                                        file_gcode.write(self.options.laseroff + '\n')
                                    Laser_ON = False
                                else:
                                    if matrice_BN[y][x+1] != N:
                                        file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                        if not self.options.laserminsw:
                                            file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False
                else:
                    for x in reversed(range(w)):
                        if matrice_BN[y][x] == N:
                            if not Laser_ON:
                                file_gcode.write('G0 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
                                if not self.options.laserminsw:
                                    file_gcode.write(self.options.laseron + '\n')
                                Laser_ON = True
                            if  Laser_ON:   #DEVO evitare di uscire dalla matrice
                                if x == 0:
                                    file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n')
                                    if not self.options.laserminsw:
                                        file_gcode.write(self.options.laseroff + '\n')
                                    Laser_ON = False
                                else:
                                    if matrice_BN[y][x-1] != N:
                                        file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                        if not self.options.laserminsw:
                                            file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False

        else: ##SCALA DI GRIGI
            for y in range(h):
                if y % 2 == 0:
                    for x in range(w):
                        if matrice_BN[y][x] != B:
                            if not Laser_ON:
                                if self.options.laserminsw:
                                    file_gcode.write('G0 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' S' + str(LaserMaxValue - matrice_BN[y][x]) +'\n')
                                else:
                                    file_gcode.write('G0 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                    file_gcode.write(self.options.laseron + ' '+ ' S' + str(LaserMaxValue - matrice_BN[y][x]) +'\n')
                                Laser_ON = True

                            if  Laser_ON:   #DEVO evitare di uscire dalla matrice
                                if x == w-1: #controllo fine riga
                                    file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n')
                                    if not self.options.laserminsw:
                                        file_gcode.write(self.options.laseroff + '\n')
                                    Laser_ON = False

                                else:
                                    if matrice_BN[y][x+1] == B:
                                        file_gcode.write('G1 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                        if not self.options.laserminsw:
                                            file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False

                                    elif matrice_BN[y][x] != matrice_BN[y][x+1]:
                                        if self.options.laserminsw:
                                            file_gcode.write('G1 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' S' + str(LaserMaxValue - matrice_BN[y][x+1]) +'\n')
                                        else:
                                            file_gcode.write('G1 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                            file_gcode.write(self.options.laseron + ' '+ ' S' + str(LaserMaxValue - matrice_BN[y][x+1]) +'\n')


                else:
                    for x in reversed(range(w)):
                        if matrice_BN[y][x] != B:
                            if not Laser_ON:
                                if self.options.laserminsw:
                                    file_gcode.write('G0 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' S' + str(LaserMaxValue - matrice_BN[y][x]) +'\n')
                                else:
                                    file_gcode.write('G0 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                    file_gcode.write(self.options.laseron + ' '+ ' S' + str(LaserMaxValue - matrice_BN[y][x]) +'\n')
                                Laser_ON = True

                            if  Laser_ON:   #DEVO evitare di uscire dalla matrice
                                if x == 0: #controllo fine riga ritorno
                                    file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n')
                                    if not self.options.laserminsw:
                                        file_gcode.write(self.options.laseroff + '\n')
                                    Laser_ON = False

                                else:
                                    if matrice_BN[y][x-1] == B:
                                        file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                        if not self.options.laserminsw:
                                            file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False

                                    elif  matrice_BN[y][x] != matrice_BN[y][x-1]:
                                        if self.options.laserminsw:
                                            file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' S' + str(LaserMaxValue - matrice_BN[y][x-1]) +'\n')
                                        else:
                                            file_gcode.write('G1 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                            file_gcode.write(self.options.laseron + ' '+ ' S' + str(LaserMaxValue - matrice_BN[y][x-1]) +'\n')



        #Configurazioni finali standard Gcode
        file_gcode.write("\n\n\n" + self.options.laseroff + '; LASER OFF\n')
        file_gcode.write('G0 X0 Y0; return home\n')
        file_gcode.close() #Chiudo il file






######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	########
def _main():
    e = GcodeExport()
    e.run()
    sys.exit()

if __name__ == "__main__":
    _main()
