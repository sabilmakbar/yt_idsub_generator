def is_number(x):
    if isinstance(x, str):
        x = x.replace(',', '')
    # invalid_number = ['nan', 'inf', '-nan', '-inf']
    try:
        float(x)
    except:
        return False
    else:
        # if x.lower() in invalid_number:
            # return False
        return True


def text2int(textnum, thousand_sep:str=".", decimal_sep:str=",", numwords:dict={}):
    units = [
        '0', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
        'sixteen', 'seventeen', 'eighteen', 'nineteen',
    ]
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']
    # ordinal_words = {'first':1, 'second':2, 'third':3, 'fifth':5, 'eighth':8, 'ninth':9, 'twelfth':12}
    # ordinal_endings = [('ieth', 'y'), ('th', '')]

    #numwords is mapper of tuples with scale and increment
    if not numwords:
        numwords['and'] = (1, 0)
        for idx, word in enumerate(units): numwords[word] = (1, idx)
        for idx, word in enumerate(tens): numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales): numwords[word] = (10 ** (idx * 3 or 2), 0) #if idx = 0, return 2, else return idx*3

    textnum = textnum.replace('-', ' ')

    current = result = 0
    curstring = ''
    onnumber = False
    lastunit = False
    lastscale = False


    def is_numword(x):
        if is_number(x):
            return True
        if word in numwords.keys():
            return True
        return False

    def from_numword(x):
        if is_number(x):
            scale = 0
            if decimal_sep in x:
              increment = float(x.replace(thousand_sep, ''))
            else: 
              increment = int(x.replace(thousand_sep, ''))
            return scale, increment
        else:
            return numwords[x]

    for word in textnum.split():
        # if word in ordinal_words:
        #     scale, increment = (1, ordinal_words[word])
        #     current = current * scale + increment
        #     if scale > 100:
        #         result += current
        #         current = 0
        #     onnumber = True
        #     lastunit = False
        #     lastscale = False
        # else:
        #     for ending, replacement in ordinal_endings:
        #         if word.endswith(ending):
        #             if not word.endswith('with'): #to escape with
        #               word = "%s%s" % (word[:-len(ending)], replacement)

        if (not is_numword(word)) or (word=="and" and not lastscale):
            if onnumber:
                # Flush the current number we are building
                curstring += repr(result + current) + " "
            curstring += word + " "
            result = current = 0
            onnumber = False      
            lastunit = False
            lastscale = False
        else:
            scale, increment = from_numword(word)
            onnumber = True

            if lastunit and (word not in scales):                                                                                                                                                                                                                                         
                # Assume this is part of a string of individual numbers to                                                                                                                                                                                                                
                # be flushed, such as a zipcode "one two three four five"                                                                                                                                                                                                                 
                curstring += repr(result + current)                                                                                                                                                                                                                                       
                result = current = 0                                                                                                                                                                                                                                                      

            if scale > 1:                                                                                                                                                                                                                                                                 
                current = max(1, current)                                                                                                                                                                                                                                                 

            current = current * scale + increment                                                                                                                                                                                                                                         
            if scale > 100:                                                                                                                                                                                                                                                               
                result += current                                                                                                                                                                                                                                                         
                current = 0                                                                                                                                                                                                                                                               

            lastscale = False                                                                                                                                                                                                              
            lastunit = False                                                                                                                                                
            if word in scales:                                                                                                                                                                                                             
                lastscale = True                                                                                                                                                                                                         
            elif word in units:                                                                                                                                                                                                             
                lastunit = True

    if onnumber:
        curstring += repr(result + current)

    return curstring
