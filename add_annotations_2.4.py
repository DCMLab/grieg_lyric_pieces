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
import os,re,sys,datetime,subprocess,csv

# conversion dictionary
durations = {"measure" : 1.0, "whole" : 1/1,
 "half" : 1/2, "quarter" : 1/4, "eighth" : 1/8, "16th" : 1/16, "32nd" : 1/32,
 "64th" : 1/64, "128th" : 1/128}

skip_tags = ['Harmony','Slur','Tempo','Tuplet','Beam','endSpanner','HairPin','Volta','Trill','Dynamic'] # Tags that can stand between a <Harmony> and the event it is attached to

regex = r"""(^(\.)?((?P<key>[a-gA-G](b*|\#*)|(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))\.)?((?P<pedal>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))\[)?(?P<numeral>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i|Ger|It|Fr))(?P<form>[%o+M])?(?P<figbass>(9|7|65|43|42|2|64|6))?(\((?P<changes>(\+?(b*|\#*)\d)+)\))?(/\.?(?P<relativeroot>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)))?(?P<pedalend>\])?(?P<phraseend>\\\\)?$|@none)"""
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


    def __init__(self,xml_file,repair=False):

        self.measure = {}           # dict to access information about each measure
        self.timesig = ''           # value of the last detected time signature
        self.irregular = False     # flag for checking the completenes of measures (split measures appear as individual tags, each with attribute 'len')
        self.substract = 0          # helps constructing correct measure numbers if incomplete measures exist
        self.len = 0                # length of the piece in ticks (quarter note = 480 ticks, whole note = 1920 ticks)
        self.tuplets = {}           # dict with id: tuplet fraction, e.g. {"1": Fraction(7/4)}
        self.repair = repair
        self.corrections = False    # if True, will result in a dump() if repair == True
        self.new_numbering = False
        self.source = xml_file
        self.piece = os.path.basename(xml_file)
        self.dir = os.path.dirname(xml_file)
        with open(xml_file, 'r') as file:
            ### Object representing the XML structure to be altered
            self.soup = BeautifulSoup(file.read(), 'xml')
        self.firststaff = self.soup.find('Part').find_next_sibling('Staff')
        self.otherstaves = self.firststaff.find_next_siblings('Staff')

        #save all tuplets
        for x in self.soup.find_all("Tuplet", id=True): # loop over all <Tuplet> tags
            if x.find('Tuplet'): # this is a nested tuplet, so the fraction has to be multiplied by that of the parent tuplet
                self.tuplets[x['id']] = Fraction(int(x.normalNotes.string), int(x.actualNotes.string)) * self.tuplets[x.find('Tuplet').string]
            else:
                self.tuplets[x['id']] = Fraction(int(x.normalNotes.string), int(x.actualNotes.string))

        measures = self.firststaff.find_all('Measure')
        #Deal with pickup measure (in that case the two first measures should have number "1")
        self.pickup = True if measures[1]['number'] == "1" else False
        if not self.pickup and measures[0].has_attr('len'):

            if self.repair:
                self.pickup = True
                print(f"{self.piece}: 1st measure has attribute len={measures[0]['len']}. Corrected its measure number from 1 to 0.")
                self.corrections = True
                self.new_numbering = True
            else:
                print(f"{self.piece}: 1st measure has attribute len={measures[0]['len']} and might be a pickup measure with erroneous measure number 1. To correct, call Piece(\'{self.source}\',True).")


        for i,x in enumerate(measures):

            if x.find('TimeSig'):
                self.timesig = f"{x.find('sigN').string}/{x.find('sigD').string}"

            if self.pickup:
                if self.new_numbering:
                    if i == 0:
                        tag = self.soup.new_tag("irregular")
                        x.append(tag)
                    else:
                        self.change_number(self,x,i)
            else:
                i += 1 # if there is no pickup, measure 1 is saved with index 1 instead of 0

            i -= self.substract
            old = x['number']
            if old != str(i) and i > 0:
                if self.irregular:
                    if old != str(i+1):
                        self.change_number(x,i+1)
                else:
                    self.change_number(x,i)



            if x.has_attr('len') and i > 0:
                l = int(Fraction(x['len']) * 1920)
                prev = i-1
                if not self.irregular:
                    self.irregular = True
                    self[i] = x # this calls self.__setitem__ which saves the measure in the measure dictionary
                elif self.measure[prev]['len'][0] + l < int(Fraction(self.timesig) * 1920):
                    sys.exit(f"{self.piece}: m. {prev} and m. {i} don't add up to a full measure. Aborting.")
                else:
                    self.substract += 1
                    self.irregular = False
                    addition = self.read_measure(i,x,self.len)
                    self.len += l
                    self.measure[prev]['len'].append(l)
                    self.measure[prev]['node'].append(x)
                    prev_l = self.measure[prev]['len'][0]
                    for k, v in addition['events'].items():
                        self.measure[prev]['events'][prev_l + k] = v
                    for k, v in addition['harmonies'].items():
                        self.measure[prev]['harmonies'][prev_l + k] = v

                    if not x.find('irregular'):

                        tag = self.soup.new_tag("irregular")
                        x.append(tag)

            elif self.irregular:
                print(f"{self.piece}: m. {i-1} is incomplete and m. {i} does not complete it. Correct manually using MuseScores \'Bar Properties\'")
                self.irregular = False
            else:
                self[i] = x # this calls self.__setitem__ which saves the measure in the measure dictionary



        for i,x in enumerate(self.soup.find_all('Harmony')):
            if not x.find('name').string:
                x.decompose()
                self.corrections = True
                if not self.repair:
                    print(f"""Empty harmony tag removed. Use Piece({self.source},True) to autorepair.""")
                else:
                    print(f"{self.piece}: Empty harmony tag permanently removed.")

        for i,x in enumerate(self.otherstaves):
            if len(x.find_all('Harmony')) > 0:
                self.corrections = True
                if self.repair:
                    self.copy_harmonies(x)
                else:
                    print(f"{self.piece} contains harmonies in Staff {i+2} with id={x['id']}. To correct, call Piece(\'{self.source}\',True).")



        lh = len(self.get_harmonies())
        ls = len(self.soup.find_all('Harmony'))

        if self.corrections:
            if self.repair:
                m = re.search(r'(.*).mscx',self.piece)
                new = "%s_repaired.mscx" % m.group(1)
                old = "%s.mscx" % m.group(1)
                print(f"{old} => {new}")
                self.dump(os.path.join(self.dir,new))
                #os.rename(self.piece,old)
                lh = len(self.get_harmonies())
                ls = len(self.soup.find_all('Harmony'))
                if lh != ls:
                    print(f"""Captured only {lh} out of the {ls} harmonies in {self.piece}. Please check the score manually.
                    The easiest way to do so is getting and copying all captured harmonies via Piece.get_harmonies() and inserting them into your text editor next to the score.
                    Then, search the score for <Harmony>: Check which result number does not correspond to the line number in the copied harmony document.""")
                #else:
                    #print(f'Captured all {ls} harmonies in {new}')
            else:
                print(f"""Captured only {lh} out of the {ls} harmonies in {self.piece}. Try autorepair using Piece('{self.source}',True)""")

###################### End of __init__ ############################

    def __getitem__(self, key):
        return self.measure[key]

    def __setitem__(self, key, knot):
        self.measure[key] = self.read_measure(key, knot,self.len)
        self.len += self.measure[key]['len'][0]

    def read_measure(self, key, knot, start):
                events = {} # dictionary holding all the rests and chords in this measure
                sec_events = {}
                harmonies = {}
                pos = 0 #pointer in ticks, 0 is beat 1 of this measure

                try:
                    length = int(Fraction(knot['len']) * 1920) #if measure has irregular length (e.g. pickup measure)
                except:
                    length = int(Fraction(self.timesig) * 1920)

                def save_events(x,track,tick):
                    value = x.find('durationType').string # note value in words such as "half" (--> conversion dictionary)
                    prev = get_sibling(x.find('durationType'),False) # previous node, potentially indication <dots>
                    sca = sum([0.5 ** i for i in range(int(prev.string)+1)]) if prev and prev.name == 'dots' else 1 # scalar depending on dots
                    sca = sca * self.tuplets[x.find('Tuplet').string] if x.find('Tuplet') else sca # altering scalar if in a tuplet
                    duration = durations[value] * 1920 * sca
                    h = ''
                    prev = get_sibling(x,False)
                    while prev and prev.name in skip_tags + ['Chord']: #Slur and Tempo are Tags which can appear between Harmony and Chord
                        if prev.name == 'Chord':
                            if not prev.find('acciaccatura'):
                                break
                        elif prev.name == 'Harmony':
                            candidates = []
                            candidates.append(prev)
                            check = get_sibling(prev,False)
                            if check and check.name == 'Harmony':
                                candidates.append(check)
                            labels = [x.find('name').string for x in candidates if x.find('name').string]
                            l = len(labels)
                            if l == 1:
                                h = labels[0]
                            elif l == 2:
                                if labels[0] == labels[1]:
                                    self.corrections = True
                                    candidates[0].decompose()
                                    if self.repair:
                                        print(f"{self.piece}: Removed identical harmony in m. {key} on tick {tick}.")
                                    else:
                                        print(f"""{self.piece}: Two identical harmonies appear in m. {key} on tick {tick}, one has been temporally deleted.
                                                To keep this change, use Piece('{self.source}',repair=True).""")
                                else:
                                    print(f"{self.piece}: Two different labels are assigned to m. {key}, tick {tick}: {labels[0]} and {labels[1]}. Please delete one.")
                            break #Harmony found, end of loop
                        prev = get_sibling(prev,False)

                    return {
                        'node': x, # needed to insert a harmony label
                        'type': x.name, # Rest or Chord? (not needed)
                        'value': value,
                        'duration': duration,
                        'harmony': h,
                        'harmony_tag':prev,
                        'voice':track,
                        'timesig':self.timesig
                        }
                pos = 0
                for i, n in enumerate(knot.find_all(['Rest','Chord'])):
                    if not n.find('acciaccatura'):
                        if n.find("track"):     #events in secondary voices to be treated later
                            track = int(n.find("track").string)
                            if not track in sec_events:
                                sec_events[track] = []
                            sec_events[track].append(n)
                        else:
                            event = save_events(n,0,pos)

                            if event['harmony'] != '':
                                harmonies[pos] = event['harmony']
                                events[pos] = event
                            elif not n.find('visible'): # invisible events get only saved if they bear a harmony --> as a precaution, no new harmonies should be attached to invisible events
                                events[pos] = event
                            pos += event['duration']
                            if abs(pos-round(pos)) <= 0.01:
                                pos = round(pos)

                for k,v in sec_events.items(): #now add events from secondary voices if they don't occur synchronously
                    pos = 0
                    orig_pos = 0
                    for e in v: # for every event in every secondary voice
                        orig_pos = pos

                        pot_tick = get_sibling(e,False)
                        while pot_tick and pot_tick.name in skip_tags + ['tick']:
                            if pot_tick.name == 'tick':
                                pos = int(pot_tick.string)-start
                                break
                            pot_tick = get_sibling(pot_tick,False)
                        event = save_events(e,k,pos)
                        if not pos in events and not e.find('visible'):
                            events[pos] = event
                        if event['harmony'] != '':
                            if not pos in harmonies:
                                harmonies[pos] = event['harmony']
                            elif harmonies[pos] == event['harmony']:
                                event['harmony_tag'].decompose()
                                self.corrections = True
                                if self.repair:
                                    print(f"{self.piece}: Removed identical harmony in m. {key} on tick {str(pos)} in voice {track +1}.")
                            else:
                                print(f"{self.piece}, m. {str(key)}, tick {str(pos)}: voice {track +1} tries to override {harmonies[pos]} with {event['harmony']}. Repair manually.")
                        pos = orig_pos
                        pos += event['duration']
                        if abs(pos-round(pos)) <= 0.01:
                            pos = round(pos)

                for i, n in enumerate(knot.find_all('tick')):
                    tick = int(n.string)-start
                    n1 = get_sibling(n)
                    if n1 and n1.name == 'Harmony':
                        h = n1.find('name').string
                        if not h:
                            n1.decompose()
                            self.corrections = True
                            if not self.repair:
                                print(f"""Empty harmony tag removed in m. {key} on tick {tick}.
                                        Dump() to new file to keep the change or use Piece(file,repair=True).""")
                            else:
                                print(f"{self.piece}: Empty harmony tag permanently removed in m. {key} on tick {tick}.")
                            continue
                        n2 = get_sibling(n1)
                        n2 = n2.name if n2 else 'endOfMeasure'
                        if not n2 in ['Chord','Rest']:
                            if not tick in harmonies:
                                harmonies[tick] = h
                            #else:
                            #    print(f"Error in score: Two harmonies set in measure {str(key)}: Trying to capture {h} at tick {str(tick)}!")

                last_tag = knot.contents[-1]
                if isinstance(last_tag, NavigableString):
                    last_tag = get_sibling(last_tag,False)
                if last_tag:
                    if last_tag.name == 'Harmony' and not get_sibling(last_tag,False).name =='tick':
                        print(f"{self.piece}, m. {key}: The <Harmony> tag containing \'{last_tag.find('name').string}\' is not properly attached to an event. Please correct manually.")
                    #else:
                        #print(last_tag.name,get_sibling(last_tag,False).name)


                return { # now the measure information is ready to be stored
                'number': knot['number'],
                'node': [knot], # harmonies are inserted here
                'len': [length], # in ticks
                'start': start, # measure's onset in ticks
                'events': events,
                'harmonies': harmonies
                }

    def change_number(self, node, n):
        old_n = node['number']
        node['number'] = str(n)
        if self.repair:
            self.corrections = True
            print(f"Correct {old_n} to {n}")
            for j,y in enumerate(self.otherstaves):
                m = y.find_all("Measure", number=old_n)
                if len(m) > 1:
                    print("Hier weiterprogrammieren")
                elif len(m) == 1:
                    m[0]['number'] = n
        else:
            print(f"measure number {old_n} should be corrected to {n}")


    def add_harmony(self, m, b, h,tic=False): # adds the harmony label h at beat b (quarter beats) of measure m

        if not tic:
            beat = int((b - 1) * 480) # calculate the beat's offset in ticks
        else:
            beat = b
        tick = self.measure[m]['start'] + beat # measure's offset
        if m == 0:
            beat = beat - (int(Fraction(self.timesig) * 1920) - self.measure[m]['len'][0])
        if not beat in self.measure[m]['harmonies'].keys():
            self.measure[m]['harmonies'][beat] = h
            ### create the new <Harmony><name>h</name></Harmony> structure
            h_tag = self.soup.new_tag("Harmony")
            h_name = self.soup.new_tag("name")
            h_name.string = h
            h_tag.append(h_name)
            newline = NavigableString('\n')

            if not beat in self.measure[m]['events']:   # if at this beat there is no event to attach the harmony to:
                ends = [self.measure[m]['start'] + l for l in self.measure[m]['len']]
                if tick > ends[-1]:
                    return f"Trying to place {h} tick {tick} in m. {m} which ends at tick {ends[-1]}."
                i = 0
                while tick > ends[i]:
                    i += 1
                node = self.measure[m]['node'][i]
                t_tag = self.soup.new_tag("tick")       #create additional <tick>offset</tick> tag
                t_tag.string = str(tick)
                node.append(h_tag)
                h_tag.insert_before(t_tag)
                h_tag.insert_before(newline)
            else: #if at this beat an event occures, attach the harmony to it
                if self.measure[m]['events'][beat]['voice'] > 0:
                    h_track = self.soup.new_tag("track")
                    h_track.string = str(self.measure[m]['events'][beat]['voice'])
                    h_tag.append(h_track)
                self.measure[m]['events'][beat]['node'].insert_before(h_tag)
                h_tag.insert_after(newline)
            return tick, h
        else:
            print(f"{self.piece}: In tick {beat} of m. {m} already holds label {self.measure[m]['harmonies'][beat]} !")


    def copy_harmonies(self,from_staff):
        for i,x in enumerate(from_staff.find_all("Measure")):
            labels = x.find_all("Harmony")
            if len(labels) > 0:
                n = int(x['number'])
                m = self.read_measure(n,x,self.measure[n]['start'])
                for tick, harmony in m['harmonies'].items():
                    self.add_harmony(n,tick,harmony,True)
                    print(f"{self.piece}, m. {n}: Moved label {harmony} to upper system.")
                for j,y in enumerate(labels): #delete tags
                    y.decompose()

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
        ######################################
        #Convert with MuseScore
        subprocess.run(["mscore","-o",filename,filename], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self = self.__init__(filename)
        return pretty_markup
        # b ∈ ['beats','ticks']   <-- andere Formate denkbar, z.B. 1.1/2 statt 1.5
    def get_harmonies(self,only_wrong=False,b='beats'):
        harmonies = []
        for m, measure in self.measure.items():
            for tick, harmony in measure['harmonies'].items():
                if b == 'ticks':
                    beat = int(tick) if type(tick) == float and tick.is_integer() else tick
                elif b == 'beats':
                    beat = tick / 480 + 1
                    beat = int(beat) if beat.is_integer() else beat

                if only_wrong:
                    alternatives = harmony.split('-')
                    for h in alternatives:
                        if not re.match(regex,h):
                            harmonies.append([m, beat, harmony])
                else:
                    harmonies.append([m, beat, harmony])
        return sorted(harmonies, key=lambda x: (x[0], x[1]))


    def remove_harmonies(self,target):
        for i, tag in enumerate(self.soup.find_all("Harmony")):
            prev = get_sibling(tag, False)
            if prev:
                if prev.name == 'tick':
                    prev.decompose()
            tag.decompose()
        self.dump(target)

########################################### End of Class Piece






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
    s = Piece(score, True)
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

def extract(dir,only_correct=True):
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            m = re.search(r'(.*).mscx$',file)
            if m:
                piece = m.group(1)
                os.chdir(subdir)
                p = Piece(file)
                print(m.group(1)+'.txt')
                if only_correct:
                    h = p.get_harmonies(True)
                    if len(h) > 1:
                        print(f'{file}\'s syntax contains errors. Skipped. You can print errors by using\np = Piece({file})\np.get_harmonies(True)')
                        continue
                h = p.get_harmonies()
                frst = h[0][2].split('.')
                if len(frst) < 3:
                    print(file + '\'s first symbol does not indicate the tonality correctly. Skipped.')
                    continue
                key = h[0][2].split('.')[1]
                with open(os.path.join(subdir, piece + '.txt'), 'w') as tsvfile:
                    tsvfile.write('@skip: 4\n')
                    tsvfile.write(f'@piece: {piece}\n')
                    tsvfile.write(f'@key: {key}\n')
                    tsvfile.write(f'@meter: {p.timesig}\n')
                    writer = csv.writer(tsvfile, delimiter='\t')
                    for l in h:
                        writer.writerow(l)

#extract('/home/jojo/Desktop/mozart/KV 279/')

def check(dir,repair=False,log='check.log'):
    os.chdir(dir)
    original = sys.stdout
    with open(log, 'w') as f:
        sys.stdout = f
        for subdir, dirs, files in os.walk(dir):
            for file in files:
                #m = re.search(r'(.*)(?<!_repaired)\.mscx$',file)
                m = re.search(r'(.*)_labelled\.mscx$',file)
                if m:
                    piece = m.group(1)
                    print(f'\nChecking {file}...')
                    p = Piece(os.path.join(subdir,file),repair)
                    h = p.get_harmonies(True)
                    if len(h) > 1:
                        [print(x) for x in h]
                    h = p.get_harmonies()
                    frst = h[0][2].split('.')
                    if len(frst) < 3:
                        print(f'{file}\'s first symbol does not indicate the tonality correctly: {h[0][2]} => {frst} Maybe the initial dot is missing.')
    sys.stdout = original
#check('/home/jojo/DCML/Grieg/mscx/')
#p = Piece('/home/jojo/Desktop/mozart2/KV 280/Mozart KV 280 i_repaired.mscx')

def add(dir,annodir,log='add_harmonies.log'):
    os.chdir(dir)
    original = sys.stdout
    with open(log, 'w') as f:
        sys.stdout = f
        print(f'add_annotations_2.4.py on {datetime.datetime.now()}\n')
        for file in os.listdir(dir):
            m = re.search(r'^op(43)n(\d*)(_repaired)?.mscx',file) # general: r'op(\d*)n(\d*)\.(.*)
            #m = re.search(r'^op12n06.mscx',file) # general: r'op(\d*)n(\d*)\.(.*)
            if m:
                name = 'op%02dn%02d' % (int(m.group(1)),int(m.group(2)))
                annotations = annodir + name + '.txt'
                if Path(annotations).is_file():
                    meta = get_meta(annotations)
                    meter = meta['@meter']
                    eight = True if meter.split('/')[1] == '8' else False
                    merge(file,annotations,name+'_labelled.mscx',skip=int(meta['@skip']),eighths=eight)
                else:
                    print(file + " has no matching annotation file.")
    sys.stdout = original
add('/home/jojo/DCML/Grieg/mscx/','/home/jojo/DCML/Grieg/korrigierte Annotations/')
#check('/home/jojo/DCML/Grieg/mscx/',True)
#p = Piece('/home/jojo/DCML/Grieg/mscx/op12n06.mscx')
#p[9]['node']
#add('/home/jojo/Documents/Code/merge_annotations_with_mscx/','/home/jojo/Documents/Code/merge_annotations_with_mscx/')
