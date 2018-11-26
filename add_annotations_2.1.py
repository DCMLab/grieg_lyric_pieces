#!/usr/bin/env python
# coding: utf-8

# ## Add harmony annotations to mscx-files (uncompressed MuseScore)
#
# For harmony textfiles in the format of the output of update_syntax_0.5.jl :
#
# @skip: 4
# @piece: op.71_no.7
# @key: Eb
# @meter: 3/4
# 1	1	.Eb.I
# 2	1	I64
# 3	1	V43(9)
# ....
#
# with annotations starting in line 5, indicating `measure beat label`.
# The first property, @skip: , indicates how many lines have to be skipped until the annotations start

# In[2]:


import pandas as pd
from bs4 import BeautifulSoup, NavigableString
from fractions import Fraction
from pathlib import Path
import os,re,sys,datetime

# conversion dictionary
durations = {"measure" : 1.0, "whole" : 1/1,
 "half" : 1/2, "quarter" : 1/4, "eighth" : 1/8, "16th" : 1/16, "32nd" : 1/32,
 "64th" : 1/64, "128th" : 1/128}


# In[3]:

def get_sibling(n,next=True):
    if next:
        if isinstance(n.next_sibling, NavigableString):
            return n.next_sibling.next_sibling
        else:
            return n.next_sibling
    else:
        if isinstance(n.previous_sibling, NavigableString):
            return n.previous_sibling.previous_sibling
        else:
            return n.previous_sibling

class Piece():

    def __init__(self,xml_file):

        self.measure = {}           # dict to access information about each measure
        self.timesig = Fraction()   # value of the last detected time signature
        self.len = 0                # length of the piece in ticks (quarter note = 480 ticks, whole note = 1920 ticks)
        self.tuplets = {}           # dict with id: tuplet fraction, e.g. {"1": Fraction(7/4)}

        with open(xml_file, 'r') as file:
            ### Object representing the XML structure to be altered
            self.soup = BeautifulSoup(file.read(), 'xml')

        #save all tuplets
        for x in self.soup.find_all("Tuplet", id=True): # loop over all <Tuplet> tags
            if x.find('Tuplet'): # this is a nested tuplet, so the fraction has to be multiplied by that of the parent tuplet
                self.tuplets[x['id']] = Fraction(int(x.normalNotes.string), int(x.actualNotes.string)) * self.tuplets[x.find('Tuplet').string]
            else:
                self.tuplets[x['id']] = Fraction(int(x.normalNotes.string), int(x.actualNotes.string))

        # Save all measure nodes from the first staff (because [0] would be the tag within the <part> declaration)
        measures = self.soup.find_all("Staff", id="1")[1].find_all('Measure')
        #Deal with pickup measure (in that case the two first measures should have number "1")
        self.pickup = True if measures[1]['number'] == "1" else False

        for i,x in enumerate(measures):

            if x.find('TimeSig'):
                self.timesig = Fraction(int(x.find('sigN').string),int(x.find('sigD').string))

            if not self.pickup:
                i += 1 # if there is no pickup, measure 1 is saved with index 1 instead of 0

            self[i] = x # this calls self.__setitem__ which saves the measure in the measure dictionary


    def __getitem__(self, key):
        return self.measure[key]

    def __setitem__(self, key, knot):

        events = {} # dictionary holding all the rests and chords in this measure
        sec_events = {}
        harmonies = {}
        pos = 0 #pointer in ticks, 0 is beat 1 of this measure

        try: # measure's length to be added to the self.len property in order to know where the next measure will start
            length = int(Fraction(knot['len']) * 1920) #if measure has irregular length (e.g. pickup measure)
        except:
            length = int(self.timesig * 1920)

        def save_events(x,track):
            value = x.find('durationType').string # note value in words such as "half" (--> conversion dictionary)
            prev = get_sibling(x.find('durationType'),False) # previous node, potentially indication <dots>
            sca = sum([0.5 ** i for i in range(int(prev.string)+1)]) if prev and prev.name == 'dots' else 1 # scalar depending on dots
            sca = sca * self.tuplets[x.find('Tuplet').string] if x.find('Tuplet') else sca # altering scalar if in a tuplet
            duration = durations[value] * 1920 * sca
            h = ''
            prev = get_sibling(x,False)
            if prev:
                p = prev
                name = p.name
                h = p.find('name').string if name == 'Harmony' else ''
            return {
                'node': x, # needed to insert a harmony label
                'type': x.name, # Rest or Chord? (not needed)
                'value': value,
                'duration': duration,
                'harmony': h,
                'voice':track
                }

        for i, n in enumerate(knot.find_all(['Rest','Chord'])):
            if n.find("track"):     #events in secondary voices to be treated later
                track = int(n.find("track").string)
                if not track in sec_events:
                    sec_events[track] = []
                sec_events[track].append(n)
            else:
                event = save_events(n,0)
                if not n.find('visible'):
                    events[pos] = event
                if event['harmony'] != '':
                    harmonies[pos] = event['harmony']
                pos += event['duration']

        for k,v in sec_events.items(): #now add events from secondary voices if they don't occur synchronously
            pos = 0
            for e in v:
                event = save_events(e,k)
                if not pos in events and not e.find('visible'):
                    events[pos] = event
                if event['harmony'] != '':
                    if not pos in harmonies:
                        harmonies[pos] = event['harmony']
                    else:
                        print(f"Error in score: Two harmonies set in measure {str(key)}, tick {str(pos)}!")
                pos += event['duration']

        for i, n in enumerate(knot.find_all('tick')):
            n1 = get_sibling(n)
            if n1 and n1.name == 'Harmony':
                n2 = get_sibling(n1)
                n2 = n2.name if n2 else 'endOfMeasure'
                if not n2 in ['Chord','Rest']:
                    tick = int(n.string)-self.len
                    if not tick in harmonies:
                        harmonies[tick] = n1.find('name').string
                    else:
                        print(f"Error in score: Two harmonies set in measure {str(key)}, tick {str(pos)}!")

        self.measure[key] = { # now the measure information is ready to be stored
        'number': knot['number'],
        'node': knot, # harmonies are inserted here
        'len': length, # in ticks
        'start': self.len, # measure's onset in ticks
        'events': events,
        'harmonies': harmonies
        }

        self.len += length

    def add_harmony(self, m, b, h): # adds the harmony label h at beat b (quarter beats) of measure m
        beat = int((b - 1) * 480) # calculate the beat's offset in ticks
        tick = self.measure[m]['start'] + beat # measure's offset


        ### create the new <Harmony><name>h</name></Harmony> structure
        h_tag = self.soup.new_tag("Harmony")
        h_name = self.soup.new_tag("name")
        h_name.string = h
        h_tag.append(h_name)
        newline = NavigableString('\n')

        if not beat in self.measure[m]['events']:   # if at this beat there is no event to attach the harmony to:
            t_tag = self.soup.new_tag("tick")       #create additional <tick>offset</tick> tag
            t_tag.string = str(tick)
            self.measure[m]['node'].append(h_tag)
            h_tag.insert_before(t_tag)
            h_tag.insert_before(newline)
        else: #if at this beat an event occures, attach the harmony to it
            if self.measure[m]['events'][beat]['voice'] > 0:
                h_track = self.soup.new_tag("track")
                h_track.string = str(self.measure[m]['events'][beat]['voice'])
                h_tag.append(h_track)
            self.measure[m]['events'][beat]['node'].insert_before(h_tag)
            h_tag.insert_after(newline)

        return tick, h_tag

    def add_space(self, s):
        space = self.soup.new_tag("harmonyY")
        space.string = str(s)
        self.soup.find("Style").insert(0, space)


    def dump(self,filename): #save the altered XML structure as filename
        ### the following code makes sure that <opening>and</closing> are written into the same line
        unformatted_tag_list = []
        for i, tag in enumerate(self.soup.find_all()):
            unformatted_tag_list.append(str(tag))
            tag.replace_with('{' + 'unformatted_tag_list[{0}]'.format(i) + '}')
        pretty_markup = self.soup.prettify().format(unformatted_tag_list=unformatted_tag_list) #writes tags into the same line

        with open(filename, "w") as file:
            file.write(pretty_markup)
        return pretty_markup


    def get_harmonies(self,b='beats'):
        harmonies = []
        for m, measure in self.measure.items():
            for tick, harmony in measure['harmonies'].items():
                if b == 'ticks':
                    beat = tick
                elif b == 'beats':
                    beat = tick / 480 + 1
                    beat = int(beat) if beat.is_integer() else beat
                harmonies.append([m, beat, harmony])
        return harmonies

    def remove_harmonies(self,target):
        for i, tag in enumerate(self.soup.find_all("Harmony")):
            prev = get_sibling(tag, False)
            if prev:
                if prev.name == 'tick':
                    prev.decompose()
            tag.decompose()
        self.dump(target)
        self = Piece(target)



########################################### End of Class Piece
s = Piece("00labelled.mscx")
s.remove_harmonies("00.mscx")
s.get_harmonies()

os.chdir("/e/Documents/DCML/Grieg/mscx")

################################################
# score = mscx-file to be annotated
# harmonies = textfile with harmonic annotations
# target = new file to write to
# spacing = optional value if you want to add spacing between the labels and the upper system (good values go from 5 to appr. 8)
# eights = should be true if the annotations work with eighth beats
################################################
def merge(score,harmonies,target, spacing = 0, eighths=False, skip = 0):
    print("\nSTART " + score)
    with open(harmonies, 'r') as file:
    #################################################################
    # parameter skiprows = 4 would mean that line 6 will be the first row of the dataframe an
    # the process will give a warning for each bad line, i.e. where the harmony symbol is followed by additional information without comment sign
    #################################################################
        an = pd.read_table(file, delim_whitespace=True, header=None, skiprows=skip, names=['measure','beat','label'], comment='?', error_bad_lines=False, warn_bad_lines=True)

    # uncomment to delete an m before measure numbers (m1 m2 etc.)
    #an['measure'] = an['measure'].apply(lambda x: int(x[1:]))

    if eighths:
        an['beat'] = an['beat'].apply(lambda x: (x - 1) / 2 + 1) #convert eighth beats into quarter beats

    s = Piece(score)
    for m, b, h in an.itertuples(index = False, name=None):
        print(s.add_harmony(m, b, h))
    if spacing != 0:
        s.add_space(spacing)
    s.dump(target)


# ### Before use
#
# * [Score] If the score has a pickup measure, make sure it is not counted, so that the first full measure has number 1
# * [Score] Clear score of erroneous empty measures
#
def get_meta(annotations):
    with open(annotations,'r') as file:
        line = file.readline()
        meta = {}
        while line[0] == '@':
            lst = line.strip().split(': ')
            meta[lst[0]] = lst[1]
            line = file.readline()
    return meta

def add(dir,annodir,log='log.txt'):
    os.chdir(dir)
    original = sys.stdout
    with open(log, 'w') as f:
        sys.stdout = f
        print(f'add_annotations_1.9.py on {datetime.datetime.now()}\n')
        for file in os.listdir(dir):
            m = re.search(r'^op43n(\d*).mscx$',file) # general: r'op(\d*)n(\d*)\.(.*)
            if m:
                name = 'op43n%02d' % int(m.group(1))
                annotations = annodir + name + '.txt'
                if Path(annotations).is_file():
                    meta = get_meta(annotations)
                    meter = meta['@meter']
                    eight = True if meter.split('/')[1] == '8' else False
                    merge(file,annotations,name+'_labelled.mscx',skip=int(meta['@skip']),eighths=eight)
                else:
                    print(file + " has no matching annotation file.")
    sys.stdout = original
