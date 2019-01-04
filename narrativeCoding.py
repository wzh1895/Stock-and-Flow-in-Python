"""

This module contains functions for interpreting narrative description of the situation {problem, hypothesis, etc.}
The first goal is to interpret the following statements:

-'The tea cup gets cold.'
-'It gets cold slower and slower.'
-'It ends up not higher than the room temperature.'

Following 'coding' paradigm, key variables that can be extracted are:

'tea cup', 'cold', 'room temperature'

In the same way, key trend that can be extracted are:

'getting cold'      -> temperature going down;
'slower and slower' -> a lowering speed;
'end up'            -> at a later temporal stage;
'not higher than'   -> a comparison, between two temperatures.

What needed here, is to create a data structure for 'process' i.e. a sequence of time, which is a 'narrative framework'.
Observation and description could be made within this structure (like a micro world). It can also be used to validate
external statement.

Remember, all SD per se says is that 'variables change over time'. Everything else is deduction, i.e. secondary statement.

Raw data{time series, visual, vocal} and narrative data =1=> mental mode (reference mode) =2=> comparison with knowledge

'Strictly speaking, for Hume, our only external impression of causation is a mere constant conjunction of phenomena,
that B always follows A, and Hume sometimes seems to imply that this is all that causation amounts to.'
--https://www.iep.utm.edu/hume-cau/#H1

"""

import pickle

file = open("processed_narratives", "rb")
processed_narratives = pickle.load(file)
file.close()

narrative1, narrative2= processed_narratives[0], processed_narratives[1]

#print('Sentences:\n',' Narrative 1:\n',narrative1[0],' Narrative 2:\n',narrative2[0],' Narrative 1:\n',narrative3[0])
#print('Tokens:\n',' Narrative 1:\n',narrative1[1],'\n',' Narrative 2:\n', narrative2[1],'\n',' Narrative 3:\n',narrative3[1],'\n')
#print('Part of speech:\n',' Narrative 1:\n',narrative1[2],'\n',' Narrative 2:\n', narrative2[2],'\n',' Narrative 3:\n',narrative3[2],'\n')
#print('Named entities:\n',' Narrative 1:\n',narrative1[3],'\n',' Narrative 2:\n', narrative2[3],'\n',' Narrative 3:\n',narrative3[3],'\n')
#print('Dependency parsing:\n',' Narrative 1:\n',narrative1[4],'\n',' Narrative 2:\n', narrative2[4],'\n',' Narrative 3:\n',narrative3[4],'\n')

NNs = []
VBZs = []

for processed_narrative in processed_narratives:
    #print(processed_narrative[2])
    for pos_word in processed_narrative[2]:
        if pos_word[1] == 'NN': # obtain all NN (Noun)s from the narratives.
            if pos_word[0] not in NNs:
                NNs.append(pos_word[0])
        if pos_word[1] == 'VB': # obtain all VBZs (3rd single verb)s from the narratives.
            if pos_word[0] not in VBZs:
                VBZs.append(pos_word[0])

print("We found the following nouns:",NNs)
print("We found the following verbs:",VBZs)
