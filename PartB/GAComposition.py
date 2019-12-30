import random
from mxlParsing import *
import math
import pandas as pd
import gc
import math


def compare_measures(m1,m2):
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
    if m1.getSos()==m2.getSos():
        return True
    else:
        return False

def similarityratio_measures(m1,m2):
    m1_notes = m1.getSos()
    m2_notes = m2.getSos()
    min_len = min(len(m1_notes),len(m2_notes))
    max_len = max(len(m1_notes),len(m2_notes))
    same_notes = 0
    for index in range(0, min_len):
        if m1_notes[index]==m2_notes[index]:
            same_notes += 1
    ratio = round(same_notes/max_len,2)
    return ratio

def get_similarity_map(measures,threshold):
    '''get similarity map given threshold for measures'''
    meas_sim_dict = {}
    for index1 in range(0,len(measures)):
        meas_sim_dict[index1]=[]
        for index2 in range(0,len(measures)):
            if index2!=index1:
                sim = similarityratio_measures(measures[index1],measures[index2])
                if sim>threshold:
                    meas_sim_dict[index1].append(index2)
    return meas_sim_dict


class GAComposition:
    measSimThresh = 0
    cooc_df = None
    simMap = None
    measMutProb = 0
    scorePop = []
    maxPop = 0
    scoreOriginal = None
    mutPerScoreThresh = 3
    #nondefinable
    scorePool = []
    candidateAmtMax = 5
    
    def __init__(self, score = None, measSimThresh = 0.70, coocPath = 'note_coocc.pickle', 
                 measMutProb = 0.1, recombProb = 0.1, maxPop = 100, mutPerScoreThresh = 2):
        self.scoreOriginal = score
        self.cooc_df = pd.read_pickle(coocPath)
        self.simMap = get_similarity_map(score.measures,measSimThresh)
        self.measSimThresh = measSimThresh
        self.measMutProb = measMutProb
        self.recombProb = recombProb
        self.maxPop = maxPop
        self.mutPerScoreThresh = mutPerScoreThresh
        #functions
        self.initPopulation()
        
    def get_measure_fitness(self, measure):
        '''get a fitness score for a measure'''
        m_score = 0
        rests = 0
        ml = measure.getSos()
        ml_len = len(ml)
        for index in range(0,ml_len-1):
            #handle naturals
            prev_note = ml[index]
            if len(ml[index])>2 and ml[index][1]=='n':
                ml[index] = ml[index][0]+ml[index][2]
            if len(ml[index+1])>2 and ml[index+1][1]=='n':
                ml[index+1] = ml[index+1][0]+ml[index+1][2]
            #can't compute rests
            if ml[index]=='0' or ml[index+1]=='0':
                rests += 1
            #get fitness
            else:
                note_score = self.cooc_df[ml[index]][ml[index+1]]
                m_score += note_score
        m_score /= (ml_len-rests)
        m_score = round(m_score,3)
        return m_score
    
    
    def get_score_fitness(self, score):
        measures = score.measures
        score_fitness = 0
        for measure in measures:
            score_fitness+=self.get_measure_fitness(measure)
        score_fitness /= len(measures)
        score_fitness = round(score_fitness,2)
        return score_fitness

    def mutateScore(self, score):
        #how many mutations
        scoreMutAmt = random.randint(1,self.mutPerScoreThresh)
        #DEBUG
        #print("mutating scoreamt: " + str(scoreMutAmt))
        #where
        for mut in range(1,scoreMutAmt):
            index = random.randint(0,score.length-1)
            meas = score.measures[index]
            self.mutateMeasure(index,meas)
                        

    def mutateMeasure(self,index,curr_measure):
        '''mutates a measure with prob measMutProb'''
        meas_sos = curr_measure.getSos()
        meas_len = len(meas_sos)
        mut_prob  = random.randint(0,100)/100
        mut_succ = False
        if mut_prob <= self.measMutProb and meas_len>1:
            while not mut_succ:
                #DEBUG
                #print("calling mutating note...")
                mut_index = random.randint(1,meas_len-1)
                note_to_mut = curr_measure.notes[mut_index]
                prev_note = curr_measure.notes[mut_index-1]
                original_note_so = note_to_mut.getSo()
                mut_succ = self.mutateNote(note_to_mut,prev_note)
                new_note_so = note_to_mut.getSo()

            #change similar notes in similar measures
            simMeasInd = self.simMap[index]
            for i in simMeasInd:
                iNotes = self.scoreOriginal.measures[i].notes
                for iNote in iNotes:
                    if iNote.getSo() == original_note_so:
                        if len(new_note_so)>2:
                            iNote.step = new_note_so[0]
                            iNote.octave = int(new_note_so[2])
                            iNote.accidental = new_note_so[1]
                        else:
                            iNote.step = new_note_so[0]
                            iNote.octave = int(new_note_so[1])
                        #change accidentla
                        iNote.accidental = None
                        
    def mutateNote(self, note, prev_note):
        '''mutates a note with probability proportional to noteoccurence'''
        #DEBUG
        #print('getting new note')
        prev_note_so = prev_note.getSo()
        if  prev_note != '0': #ignore rests
            #handle naturals
            if len(prev_note_so)>2 and prev_note_so[1]=='n':
                prev_note_so = prev_note_so[0]+prev_note_so[2]
             #get candidates
            #print(prev_note)
            candidates = self.cooc_df[prev_note_so]
            candidates = candidates[candidates>0]
            candidates = candidates.sort_values(ascending=False)
            #get new note
            newnote_index = random.randint(0,self.candidateAmtMax)
            new_note_so = candidates.index[newnote_index]
            #change note
            #DEBUG
            #print('changing note')
            if len(new_note_so)>2:
                note.step = new_note_so[0]
                note.octave = int(new_note_so[2])
                note.accidental = new_note_so[1]
            else:
                note.step = new_note_so[0]
                note.octave = int(new_note_so[1])
            #change accidentla
            note.accidental = None
            return True
        else:
            return False

        
    def initPopulation(self):
        for i in range (0, self.maxPop):
            s = self.scoreOriginal.copyScore()
            self.mutateScore(s)
            self.scorePop.append(s)
            #DEBUG
            #print(self.get_score_fitness(s))
        
    def mutateGeneration(self):
        self.scorePool = []
        #copy the parents
        for s in self.scorePop:
            self.scorePool.append(s.copyScore())
        #mutate the offspring
        for s in self.scorePool:
            self.mutateScore(s)
        #add parents to pool
        for s in self.scorePop:
            self.scorePool.append(s.copyScore())
        #DEBUG
        #for s in self.scorePool:
        #    print(self.get_score_fitness(s))
        #print('-----')
            
    def survivalSelection(self):
        self.scorePop = []
        score_df = pd.DataFrame()
        for index in range(0,len(self.scorePool)):
            scoretorate = self.scorePool[index]
            fitScore = self.get_score_fitness(scoretorate)
            #debug
            #print(fitScore)
            score_df = score_df.append([fitScore])
        #DEBUG
        #print(score_df)
        #print('.....')
        score_df.reset_index()
        score_rank_df = score_df.sort_values(by=0)
        for i in range(0,self.maxPop):
            good_score_idx = score_rank_df.index[i]
            #DEBUG
            #print("Goodscore:")
            #print(good_score_idx)
            scoreToAppend = self.scorePool[good_score_idx]
            self.scorePop.append(scoreToAppend)
        self.scorePool = []
        gc.collect()
    
    def evolve(self,generations=100):
        for i in range(0,generations):
            self.mutateGeneration()
            self.survivalSelection()
        
    def getTop3(self):
        score_df = pd.DataFrame()
        top3 = []
        for index in range(0,len(self.scorePop)):
            scoretorate=self.scorePop[index]
            fitScore = self.get_score_fitness(scoretorate)
            #debug
            #print(fitScore)
            score_df = score_df.append([fitScore])
        score_df.reset_index()
        #debug
        #print(score_df)
        score_rank_df = score_df.sort_values(by=0)
        
        for i in range(0,3):
            good_score_idx = score_rank_df.index[i]
            top3.append(self.scorePop[good_score_idx])
        return top3