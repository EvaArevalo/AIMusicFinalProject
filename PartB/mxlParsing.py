from enum import Enum
import math
import music21 as m21
import random
import xml.etree.cElementTree as ET

####CLASSES#####

class NoteTypes(Enum):
	'''Class defining types of notes'''
	whole = 1
	half = 2
	quarter = 4
	eight = 8
	sixteenth = 16
	thirtysecond = 32

class NoteLetters(Enum):
    '''Class representing a musical note'''
    C = 0
    D = 2
    E = 4
    F = 6
    G = 8
    A = 10
    B = 12

class Score:
    '''An array of measures'''
    measures = []
    length = 0
    ts = None
    
    def __init__(self,measures,ts=None):
        self.measures = measures
        self.length = len(measures)
        self.ts = ts
    
    def copyScore(self):
        newMeasures = []
        for measure in self.measures:
            m = measure.copyMeasure()
            newMeasures.append(m)  
        newScore = Score(newMeasures)
        
        return newScore

    def printScore(self):
        for m in self.measures:
            m.printMeasure()

class Note:
    '''Class representing a musical note'''
    notetype = None
    step = ''
    octave = 0
    so = None
    tie = None
    accidental = None
    dot = False
    
    def __init__(self,notetype,step,octave,tie,accidental,dot):
        self.notetype = notetype
        self.step = step
        self.octave = int(octave)
        self.tie = tie
        self.accidental = accidental
        self.dot = dot
        
    def getSo(self):
        if self.accidental:
            so = self.step + self.accidental + str(self.octave)
        else:
            
            so = self.step + str(self.octave)
        return so
    
    def printNote(self):
        if self.step=='':
            print('Note: ' + 'rest' + ' / ' +
              str(self.notetype))
        else:
            print('Note: ' + str(self.getSo()) + ' / ' +
              str(self.notetype) + ' / ' +
              str(self.tie)) 
            
    def addOctaves(self,addOct):
        self.octave += addOct
        
    def copyNote(self):
        ncopy = Note(self.notetype,self.step,self.octave,self.tie,self.accidental,self.dot)
        return ncopy
    
    def addSemiTones(self,semiTToAdd):
        
        #get relative position of new note
        newVal = getattr(NoteLetters,self.step).value + semiTToAdd
        #DEBUG
        #print(newVal)
        
        #handle semitones first
        if (semiTToAdd%2!=0):
            
            if self.accidental == '#':
                self.accidental = None
                newVal += 1

            elif self.accidental == 'b':
                self.accidental = None
                newVal -= 1
            
            elif not self.accidental:
                self.accidental = '#'
                newVal -= 1
                
            #natural, assumes sharps in score
            else:
                self.accidental = None
                newVal -= 1

       
        #Change step
        self.step = NoteLetters(newVal% 14).name
        
        #change octave
        self.octave += math.floor(newVal/14)   

class Measure:
    '''Class representing a measure'''
    notes = []
    
    def __init__(self,notes):
        self.notes = notes
    
    def getSos(self):
        sos = []
        for note in self.notes:
            sos.append(note.getSo())
        return sos
    
    def getNotetypes(self):
        notetypes = []
        for note in self.notes:
            notetypes.append(note.notetype)
        return notetypes 
    
    def getTies(self):
        ties = []
        for tie in self.notes:
            ties.append(note.tie)
        return ties 
    
    def printMeasure(self):
        for note in self.notes:
            note.printNote()
            
    def getNotes(self):
        return notes

    def copyMeasure(self):
        mcopy = Measure(self.notes)
        return mcopy

####XML DECODING####

def get_ts_xml(root):
    '''Gets time signature for a musicxml file.
    Input: Root of XML Tree
    Output:top and bottom numbers of the Time signature'''
    time = root.find('.//time')
    top = int(time.find(".//beats").text)
    bottom = int(time.find(".//beat-type").text)
    return top,bottom

def get_bpm_xml(root):
    '''Gets beats per minute as well as type of beats for a musicxml file.
    Input: Root of XML Tree
    Output: beats per minute, noteType'''
    metronome = root.find('.//metronome')
    beats_per_min = int(metronome.find('.//per-minute').text)
    beat_type = metronome.find('.//beat-unit').text
    #beat_type = getattr(NoteTypes, str(beat_type))
    return beats_per_min, beat_type

def decode_xml_note(xml_note):
    '''Gets note type, step, octave and tie type'''
    try:
        notetype = xml_note.find('.//type').text
    except:
        notetype = None
    try:
        step = xml_note.find('.//step').text
    except:
        step = ''
    try:
        octave = xml_note.find('.//octave').text
    except:
        octave = 0
    try:
        tie = xml_note.find('.//tie').get('type')
    except:
        tie = None
    if xml_note.find('.//dot') != None:
        dot = True
    else:
        dot = False
    try:
        accidental = xml_note.find('.//accidental').text
        if accidental == 'natural':
            accidental = 'n'
        if accidental == 'flat':
            accidental = 'b'
        if accidental == 'sharp':
            accidental = '#'
            
    except:
        accidental = None
        
    note = Note(notetype,step,octave,tie,accidental,dot)
    #DEBUG
    #note.printNote()
    
    return note

# return all notes in a measure
def get_meas_notes_xml(xml_measure_notes):
    notes = []
    for xml_note in xml_measure_notes:
        note = decode_xml_note(xml_note)
        if note.notetype:
            notes.append(note)
        #DEBUG
        #note.printNote()
    return notes

def xmlToScore(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    xml_measures = root.findall('.//measure')
    measures = []

    for xml_measure in xml_measures:
        measure = Measure(get_meas_notes_xml(xml_measure))
        if not measure.getSos()==['0']:
            measures.append(measure)

    top,bottom = get_ts_xml(root)
    ts = m21.meter.TimeSignature(str(top)+'/'+str(bottom))
            
    return Score(measures,ts)
    

###MANIPULATION FUNCTIONS####

def compare_notes(n1,n2):
    '''returns the difference in semitones between 2 notes'''
    val1 = getattr(NoteLetters,n1.step).value
    val2 = getattr(NoteLetters,n2.step).value
    difference = val2 - val1
    #add octaves
    difference += (n2.octave - n1.octave) * 14
    #add accidentals
    if (n1.accidental):
        if n1.accidental == '#':
            difference-=1
        elif n1.accidental == 'b':
            difference+=1
        #naturals,assumes the sheet music has flat alterations only
        else:
            difference+=1
    if (n2.accidental):
        if n1.accidental == '#':
            difference+=1
        elif n1.accidental == 'b':
            difference-=1
        #naturals,assumes the sheet music has flat alterations only
        else:
            difference-=1
    return difference

def compare_measures(m1,m2):
    '''compares measure m1 and m2, returns the average of the differences in semitones between their notes'''
    measure_diff = 0
    rests = 0
    m1_notes = m1.notes
    m2_notes = m2.notes
    min_len = min(len(m1_notes),len(m2_notes))
    for index in range(0, min_len):
        if m1_notes[index]=='0' or m2_notes[index]=='0':
            rests += 1
        note_diff = compare_notes(m1_notes[index],m2_notes[index])
        measure_diff+=note_diff
    measure_diff /= (min_len-rests)
    measure_diff = round(measure_diff,2)
    return measure_diff   

def checkeq_measures(m1,m2):
    '''Returns True if t2o measures are equal, False otherwise'''
    if m1.getSos()==m2.getSos():
        return True
    else:
        return False

def get_inverted_measure(measure):
    '''returns inversion of the measure'''
    #get first note
    inv_notes = []
    prevNoteNew = measure.notes[0].copyNote()
    if prevNoteNew.step!= '':
        prevNoteNew.addSemiTones(-14)
    #DEBUG
    #prevNoteNew.printNote()
    inv_notes.append(prevNoteNew)
    prevNoteOg = measure.notes[0].copyNote()
    
    for nextNoteOg in measure.notes[1:]:
        #handle rests
        if nextNoteOg.step == '':
            nextNoteNew = nextNoteOg.copyNote()
        else:
             #if previous measure is a rest
            if prevNoteOg.step!='':
                nextNoteNew = Note(nextNoteOg.notetype,prevNoteNew.step,prevNoteNew.octave,nextNoteOg.tie,nextNoteOg.accidental,nextNoteOg.dot)
                diff = compare_notes(prevNoteOg,nextNoteOg)
            else:
                nextNoteNew = nextNoteOg.copyNote()
                diff = 14
            nextNoteNew.addSemiTones(-diff)
        inv_notes.append(nextNoteNew)
        prevNoteOg = nextNoteOg
        prevNoteNew = nextNoteNew
            #DEBUG 
            #print(diff)
            #prevNoteNew.printNote()

    inv_meas = Measure(inv_notes)
    return inv_meas
    

####MUSIC21#####
    
def measures_to_m21Part(measures):
    '''Builds a Score in m21 format from array of Measure types'''
    
    score = None
    score = m21.stream.Part()

    for measure in measures:
        measure_notes = measure.notes
        s1 = m21.stream.Measure()
        
        #add ts to first measure
        #if not score:
            #s1.timeSignature = ts
        
        for n in measure_notes:
            #handle rests
            if n.step == '':
                s1.append(m21.note.Rest(type=n.notetype))
            #notes
            else:
                m21Note = m21.note.Note(n.getSo(),type=n.notetype, dots=n.dot)
                if n.tie:
                    m21Note.tie = m21.tie.Tie(n.tie)
                
                s1.append(m21Note)
        score.append(s1)
        
    return score

def build_m21Score_1p(part1,title,ts):
    '''builds a m21 score from 1 part'''
    clef1 = m21.clef.TrebleClef()
    clef1.offset = 0.0
    part1.offset = 0.0
    part1.id = 'mainPart'
    score = m21.stream.Score([clef1, part1])
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = title
    score.timeSignature = ts
    #s2.duration.quarterLength

    return score

def build_m21Score_2p(part1,part2,title,ts):
    '''builds a m21 score from 2 parts'''
    clef1 = m21.clef.TrebleClef()
    clef1.offset = 0.0
    part1.offset = 0.0
    part1.id = 'mainPart'

    clef2 = m21.clef.BassClef()
    clef2.offset = 0.0
    part2.offset = 0.0
    part2.id = 'accPart'

    score = m21.stream.Score([clef1, part1, clef2, part2])
    score = m21.stream.Score([clef1, part1])
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = title
    score.timeSignature = ts
    
    #s2.duration.quarterLength

    return score