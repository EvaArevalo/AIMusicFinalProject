from enum import Enum
import math


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

class Note:
    '''Class representing a musical note'''
    notetype = None
    step = ''
    octave = 0
    so = None
    tie = None
    accidental = None
    
    def __init__(self,notetype,step,octave,tie,accidental):
        self.notetype = notetype
        self.step = step
        self.octave = int(octave)
        self.tie = tie
        self.accidental = accidental
        
    def get_so(self):
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
            print('Note: ' + str(self.get_so()) + ' / ' +
              str(self.notetype) + ' / ' +
              str(self.tie))
            
    def addOctaves(self,addOct):
        self.octave += addOct
        
    def copyNote(self):
        ncopy = Note(self.notetype,self.step,self.octave,self.tie,self.accidental)
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

       
        #Change step
        self.step = NoteLetters(newVal% 14).name
        
        #change octave
        self.octave += math.floor(newVal/14)   


class Measure:
    '''Class representing a measure'''
    notes = []
    
    def __init__(self,notes):
        self.notes = notes
    
    def get_sos(self):
        sos = []
        for note in self.notes:
            sos.append(note.get_so())
        return sos
    
    def get_notetypes(self):
        notetypes = []
        for note in self.notes:
            notetypes.append(note.notetype)
        return notetypes 
    
    def get_ties(self):
        ties = []
        for tie in self.notes:
            ties.append(note.tie)
        return ties 
    
    def printMeasure(self):
        for note in self.notes:
            note.printNote()
            
    def get_notes(self):
        return notes

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
    try:
        accidental = xml_note.find('.//accidental').text
        if accidental == 'natural':
            accidental = '*'
        if accidental == 'flat':
            accidental = 'b'
        if accidental == 'sharp':
            accidental = '#'
            
    except:
        accidental = None
        
    note = Note(notetype,step,octave,tie,accidental)
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

def get_inverted_measure(measure):
    
    #get first note
    inv_notes = []
    prevNoteNew = measure.notes[0].copyNote()
    prevNoteNew.addSemiTones(-14)
    #DEBUG
    #prevNoteNew.printNote()
    inv_notes.append(prevNoteNew)
    prevNoteOg = measure.notes[0].copyNote()
    
    for nextNoteOg in measure.notes[1:]:
        nextNoteNew = Note(nextNoteOg.notetype,prevNoteNew.step,prevNoteNew.octave,nextNoteOg.tie,nextNoteOg.accidental)
        diff = compare_notes(prevNoteOg,nextNoteOg)
        nextNoteNew.addSemiTones(-diff)
        inv_notes.append(nextNoteNew)
        prevNoteOg = nextNoteOg
        prevNoteNew = nextNoteNew
        #DEBUG 
        #print(diff)
        #prevNoteNew.printNote()

    inv_meas = Measure(inv_notes)
    return inv_meas
    