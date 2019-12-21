from enum import Enum

class NoteTypes(Enum):
	'''Class defining types of notes'''
	whole = 1
	half = 2
	quarter = 4
	eight = 8
	sixteenth = 16
	thirtysecond = 32

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
        self.octave = octave
        self.tie = tie
        if accidental:
            self.so = step + accidental+ str(octave)
        else:
            self.so = step + str(octave)
        self.accidental = accidental
    
    def printNote(self):
        if self.step=='':
            print('Note: ' + 'rest' + ' / ' +
              str(self.notetype))
        else:
            print('Note: ' + str(self.so) + ' / ' +
              str(self.notetype) + ' / ' +
              str(self.tie))
            
class Measure:
    '''Class representing a measure'''
    notes = []
    
    def __init__(self,notes):
        self.notes = notes
    
    def get_sos(self):
        sos = []
        for note in self.notes:
            sos.append(note.so)
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
        if notetype == '16th':
            notetype = 'sixteenth'
        elif notetype == '32nd':
            notetype = 'thirtysecond'
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