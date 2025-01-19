from PIL import Image
import os
import random
import numpy as np
import cv2
import imutils
import csv
import time
from tqdm import tqdm

# Characters of Letters and Numbers in Plates
numbers = [str(i) for i in range(0, 10)]
# provinces = ['BAM', 'BDG', 'BDN', 'BLH', 'DYK', 'FRH', 'FYB', 'GAZ', 'GHR', 'HEL','HRT', 'JZJ', 'KBL,'KDR', 'KDZ', 'KNR','KPS', 'KST', 'LGM',
# 'LGR', 'NGR', 'NRZ', 'NUR', 'ORZ', 'PAK', 'PJR', 'PKT', 'PRN', 'SAM', 'SRP', 'TAK', 'WDK, 'ZBL',

# Fonts and Templates
# fonts = [font.split('.')[0] for font in os.listdir('../Fonts') if not font.endswith('.csv')]
fonts = ['Dari']
fontsE = ['English']
dari_letters = []
english_letters = []  
templates = [os.path.basename(os.path.splitext(template)[0]) for template in os.listdir('../templates') if template.endswith('.png')and template not in ['Diplomatic.png']]
# templates = ['template-base']

# Noises
noises = os.listdir('../Noises')
# transformations 
transformations = ['rotate_right', 'rotate_left', 'zoom_in', 'zoom_out', 'prespective_transform']

# Count of permutations
permutations = 1

# Generateplate array from string 
# (کابل 37853 -> ['کابل','3', '7', '8', '5', '3'])
def plateFromName (nameStr):
    numbers = []
    letters = []
    
    for char in nameStr:
        if char.isnumeric(): numbers.append(char)
        else: letters.append(char)

    return [ ''.join(letters) ,*numbers[:2], *numbers[2:]]

# Returns a plate as a string
def getPlateName(n1, n2, l, n3, n4, n5):
    return f'{n1}{n2}{l}{n3}{n4}{n5}'

# Returns Address of a glyph image given font, and glyph name
def getGlyphAddress(font, glyphName):
    return f'../Glyphs/{font}/{glyphName}.png'

def getGlyphAddressE(font, glyphName):
    return f'../Glyphs/English/{glyphName}.png'

# Returns an array containing a plate's letter and numbers:
# [Province, number1, number2 , number3, number4, number5]
def getNewPlate():  
    return [random.choice(letters),
            random.choice(numbers), 
            random.choice(numbers),
            random.choice(numbers), 
            random.choice(numbers),
            random.choice(numbers)]

    # return plateFromName('کابل 37853')

# Genrate Noise
def applyNoise (plate):
    background = plate.convert("RGBA")
    noisyTemplates = []
    for noise in noises:
        newPlate = Image.new('RGBA', (1200,529), (0, 0, 0, 0))
        newPlate.paste(background, (0,0))
        noise = Image.open(os.path.join('../Noises/', noise)).convert("RGBA")
        newPlate.paste(noise, (0, 0), mask=noise)
        noisyTemplates.append(newPlate)
    return noisyTemplates

# Generate Transformations of plates
def applyTransforms (plate):
    transformedTemplates = []
    plate = np.array(plate)
    
    # Rotating to clockwise
    for _ in range(3):
        result = imutils.rotate_bound(plate, random.randint(2,15))
        result = Image.fromarray(result)
        transformedTemplates.append(result)

    # Rotating to anticlockwise
    for _ in range(3):
        result = imutils.rotate_bound(plate, random.randint(-15,-2))
        result = Image.fromarray(result)
        transformedTemplates.append(result)
    
    # Scaling up
    for _ in range(3):
        height, width, _ = plate.shape
        randScale = random.uniform(1.1, 1.3)
        result = cv2.resize(plate, None, fx=randScale, fy=randScale, interpolation = cv2.INTER_CUBIC)
        result = Image.fromarray(result)
        transformedTemplates.append(result)
    
    # Scaling down
    for _ in range(3):
        height, width, _ = plate.shape
        randScale = random.uniform(0.2, 0.6)
        result = cv2.resize(plate, None, fx=randScale, fy=randScale, interpolation = cv2.INTER_CUBIC)
        result = Image.fromarray(result)
        transformedTemplates.append(result)


    return transformedTemplates

idCounter = 0
fontsProgBar = tqdm(total=len(fonts)*len(templates)*permutations*len(noises)*(len(transformations)-1)*3, desc='Generating Plate...')
for font in fonts:
    Folder = 'Generated Number Plate'
    # Create font directory if not exists
    if not os.path.exists(Folder): os.mkdir(Folder)
    # time.sleep(0.1)

    # Getting the letters list from nameMap csv
    letters = []
    with open(f'../Fonts/{font}_namesMap.csv') as nameMapCsv:
        reader = csv.reader(nameMapCsv)
        next(reader) # Skipping header
        letters = [rows[1] for rows in reader]
        
    # Load English letters from the CSV file
    english_letters = []
    with open('../Fonts/English_namesMap.csv') as nameMapCsvE:
        reader = csv.reader(nameMapCsvE)
        next(reader)
        for row in reader: # Skipping header
            english_letters.append(row[1])

    for template in templates:
        for i in range(permutations):
            idCounter += 1

            # Generate a plate as an array
            dari_plate = getNewPlate()
            dari_plate_name = getPlateName(*dari_plate)

            # Get Glyph images of Dari plate characters
            dari_glyph_images = []
            for glyph in dari_plate:
                glyph_image = Image.open(getGlyphAddress(font, glyph)).convert("RGBA")
                dari_glyph_images.append(glyph_image)
  
            # Generate a plate with English characters for the English part
            english_plate = dari_plate.copy()
            for j, char in enumerate(english_plate):
                if char in dari_letters:
                    english_plate[j] = random.choice(english_letters)
            
            # Get Glyph images of English plate characters
            english_glyph_images = []
            for glyph in english_plate:
                glyph_image = Image.open(getGlyphAddressE(font, glyph)).convert("RGBA")
                english_glyph_images.append(glyph_image)
            
            # Create a blank image with size of templates 
            # and add the background and glyph images
            new_plate = Image.new('RGBA', (1200, 529), (0, 0, 0, 0))
            background = Image.open(f'../Templates/{template}.png').convert("RGBA")
            new_plate.paste(background, (0, 0))
            # adding Dari glyph images with 11 pixel margin
            w = 0
            for i, glyph in enumerate(dari_glyph_images):
                if i == 2:
                    new_plate.paste(glyph, (70 + w, 30), mask=glyph)
                else:
                    new_plate.paste(glyph, (70 + w, 30), mask=glyph)
                w += glyph.size[0] + 11
            # adding English glyph images below Dari glyphs with 11 pixel margin
            w = 0
            for i, glyph in enumerate(english_glyph_images):
                if i == 2:
                    new_plate.paste(glyph, (70 + w, 300), mask=glyph)
                else:
                    new_plate.paste(glyph, (70 + w, 300), mask=glyph)
                w += glyph.size[0] + 11

            idCounter += 1
            # Save Plate (Dari and English parts)
            _new_plate = new_plate.resize((1200, 529), Image.ANTIALIAS)
            fontsProgBar.update(1)
            _new_plate.save(f"{Folder}/{dari_plate_name}_{template.split('-')[1]}{random.randint(0, 20)}{idCounter}.png")

            # newPlate.show(f"{font}/{plateName}_{template.split('-')[1]}.png")
            idCounter += 1
            noisyTemplates = applyNoise(_new_plate)
            for noisyTemplate in noisyTemplates:
                idCounter += 1
                fontsProgBar.update(1)
                _noisyTemplate = noisyTemplate.resize((1200,529), Image.ANTIALIAS)
                _noisyTemplate.save(f"{Folder}/{dari_plate_name}_{template.split('-')[1]}{random.randint(0,20)}{idCounter}.png")
                transformedTemplates = applyTransforms(noisyTemplate)
                for transformedTemplate in transformedTemplates:
                    idCounter += 1
                    _transformedTemplate = transformedTemplate.resize((1200,529), Image.ANTIALIAS)
                    fontsProgBar.update(1)
                    _transformedTemplate.save(f"{Folder}/{dari_plate_name}_{template.split('-')[1]}{random.randint(0,20)}{idCounter}.png")
        fontsProgBar.update(1)
    fontsProgBar.update(1)
fontsProgBar.update(1)

fontsProgBar.close()
