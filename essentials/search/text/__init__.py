class weights:

    def __init__(self):
        self.by_letter = 5
        self.by_order = 3
        self.by_length = 2
        self.by_match = 6
        self.by_best = 5
        self.by_order_lowered = 5
        self.score_limit = 0.5

class reason:
    
    def __init__(self):
        self.decay = 1
        self.weights = weights()
        self.weights.by_length = 2

    def compare_words(self, word1, word2):

        case = {'score': 0, 'tests': 0, "input": [word1, word2]}

        if len(word1) >= len(word2):
            longest = word1
            shortest = word2
        else:
            longest = word2
            shortest = word1

        by_order_forward = 0
        i = 0
        for letter in longest:
            try:
                if shortest[i] == letter:
                    by_order_forward += 1
            except:
                continue
            i += 1
        by_order_forward = by_order_forward/len(longest)

        by_order_reverse = 0
        i = 0
        for letter in shortest:
            try:
                if longest[i] == letter:
                    by_order_reverse += 1
            except:
                continue
            i += 1

        by_order_reverse = by_order_reverse/len(shortest)

        case['by_order'] = [by_order_forward, by_order_reverse, (by_order_forward + by_order_reverse)/2]
        case['score'] += (case['by_order'][2] * self.weights.by_order)
        case['tests'] += self.weights.by_order

        # ____________________________________________________________

        by_order_forward = 0
        i = 0
        for letter in longest:
            try:
                if shortest[i].lower() == letter.lower():
                    by_order_forward += 1
            except:
                continue
            i += 1
        by_order_forward = by_order_forward/len(longest)

        by_order_reverse = 0
        i = 0
        for letter in shortest:
            try:
                if longest[i].lower() == letter.lower():
                    by_order_reverse += 1
            except:
                continue
            i += 1
        by_order_reverse = by_order_reverse/len(shortest)

        case['by_order_lowered'] = [by_order_forward, by_order_reverse, (by_order_forward + by_order_reverse)/2]
        case['score'] += (case['by_order_lowered'][2] * self.weights.by_order_lowered)
        case['tests'] += self.weights.by_order_lowered

        # ____________________________________________________________

        by_letter = 0


        for letter in longest:
            if letter in shortest:
                by_letter += 1

        by_letter = by_letter/len(longest)


        by_letter_l = 0

        for letter in longest:
            if letter.lower() in shortest.lower():
                by_letter_l += 1

        by_letter_l = by_letter_l/len(longest)

        case['by_letter'] = [by_letter, by_letter_l, (by_letter + by_letter_l)/2]
        case['score'] += (case['by_letter'][2] * self.weights.by_letter)
        case['tests'] += self.weights.by_letter

        # ____________________________________________________________

        by_length = 0

        dist = abs(len(word1) - len(word2))
        score = (1/1.15)**(0.75*dist)

        case['by_length'] = score
        case['score'] += (score * self.weights.by_length)
        case['tests'] += self.weights.by_length

        # ____________________________________________________________

        

        case['score'] = case['score']/case['tests']


        case['result'] = case['score'] >= self.weights.score_limit

        return case

    def word_to_phrase(self, word, phrase):
        case = {"score": 0, "tests": 0, "best": None, "scores": []}
        matched = 0
        x_match = 0
        results = 0
        tests = 0
        for cut in phrase.split(" "):
            result = self.compare_words(word, cut)
            results += result['score']
            tests += 1
            if case['best'] is None:
                case['best'] = result
            else:
                if case['best']['score'] < result['score']:
                    case['best'] = result
            
            case['scores'].append(result['score'])
            case['score'] += result['score']
            case['tests'] += 1

            if word in cut:
                matched += 1

            if word.lower() in cut.lower():
                x_match += 1

        case['score'] += (results/tests)
        case['tests'] += 1

        case['score'] += (matched/len(phrase.split(" ")))*self.weights.by_match
        case['tests'] += self.weights.by_match

        case['score'] += (x_match/len(phrase.split(" ")))*self.weights.by_match
        case['tests'] += self.weights.by_match

        case['score'] += (case['best']['score'])*self.weights.by_best
        case['tests'] += self.weights.by_best

        case['score'] = case['score']/case['tests']
        case['result'] = case['score'] >= self.weights.score_limit

        return case

    def phrase_to_phrase(self, phrase1, phrase2):
        case = {"score": 0, "tests": 0, "input": [phrase1, phrase2]}

        if phrase1 == phrase2:
            case['score'] = 1
            case['tests'] = 1
            case['result'] = case['score'] >= self.weights.score_limit
            return case
        elif phrase1.lower() == phrase2.lower():
            case['score'] = 0.8
            case['tests'] = 1
            case['result'] = case['score'] >= self.weights.score_limit
            return case

        if len(phrase1) >= len(phrase2):
            longest = phrase1
            shortest = phrase2
        else:
            longest = phrase2
            shortest = phrase1


        matches = 0
        x_match = 0
        by_order = 0
        i = 0
        for word in longest.split(" "):
            
            if word in shortest:
                matches += 1

            if word.lower() in shortest.lower():
                x_match += 3
            
            try:
                if shortest.split(" ")[i] == word:
                    by_order += 1
            except:
                continue

            i += 1

        case['score'] += (by_order/len(longest.split(" "))) * self.weights.by_order
        case['tests'] += self.weights.by_order

        case['score'] += (matches/len(longest.split(" "))) * self.weights.by_match
        case['tests'] += self.weights.by_match

        case['score'] += (x_match/len(longest.split(" "))) * self.weights.by_match
        case['tests'] += self.weights.by_match

        matches = 0
        x_match = 0
        by_order = 0
        i = 0

        for word in shortest.split(" "):
            
            if word in longest:
                matches += 1

            if word.lower() in longest.lower():
                x_match += 1
            
            try:
                if longest.split(" ")[i] == word:
                    by_order += 1
            except:
                continue

            i += 1
        
        case['score'] += (by_order/len(longest.split(" "))) * self.weights.by_order
        case['tests'] += self.weights.by_order

        case['score'] += (matches/len(longest.split(" "))) * self.weights.by_match
        case['tests'] += self.weights.by_match

        case['score'] += (x_match/len(longest.split(" "))) * self.weights.by_match
        case['tests'] += self.weights.by_match
        
        
        by_length = 0

        dist = abs(len(phrase1) - len(phrase2))
        score = (1/1.15)**(0.75*dist)

        case['by_length'] = score
        case['score'] += (score * self.weights.by_length)
        case['tests'] += self.weights.by_length


        case['score'] = case['score']/case['tests']
        case['result'] = case['score'] >= self.weights.score_limit

        return case

    def phrase_to_phrase_arry(self, phrase, array):
        case = {"best": None, "sorted": [], "input": [phrase, array[:5]]}

        for phrase2 in array:
            results = self.phrase_to_phrase(phrase, phrase2)
            results['phrases'] = phrase, phrase2

            if case['best'] is None:
                case['best'] = results
            else:
                if case['best']['score'] < results['score']:
                    case['best'] = results
            case['sorted'].append(results)
        
        case['sorted'] = sorted(case['sorted'], key = lambda i: i['score'])
        case['sorted'].reverse()

        return case

    def word_to_phrase_arry(self, word, array):
        case = {"best": None, "sorted": [], "input": [word, array[:5]]}

        for phrase2 in array:
            results = self.word_to_phrase(word, phrase2)
            results['input'] = [word, phrase2]
            if case['best'] is None:
                case['best'] = results
            else:
                if case['best']['score'] < results['score']:
                    case['best'] = results
            case['sorted'].append(results)
        
        case['sorted'] = sorted(case['sorted'], key = lambda i: i['score'])
        case['sorted'].reverse()

        return case

    def auto(self, in1, in2):
        if in1.count(" ") > 0:
            if type(in2) == type([]):
                return self.phrase_to_phrase_arry(in1, in2)
            else:
                if in2.count(" ") > 0:
                    return self.phrase_to_phrase(in1, in2)
                else:
                    return self.word_to_phrase(in2, in1)
        else:
            if type(in2) == type([]):
                return self.word_to_phrase_arry(in1, in2)
            else:
                if in2.count(" ") > 0:
                    return self.word_to_phrase(in1, in2)
                else:
                    return self.compare_words(in1, in2)


class ranker:
    def __init__(self):
        pass

    def rank(self, in1, data, key="phrase", add_points_key=None):
        all_points = 0

        for item in data:
            points = 0
            try:
                phrase = item['phrase']
                if add_points_key is not None:
                    points += item[add_points_key]
            except:
                print("Error on structure-")
                print("ranker uses list of dict - [{'key': '.....'}, {'key..}]")
                if add_points_key is not None:
                    print("ensure", add_points_key, "is in dict")
                raise SyntaxError("Structe Error")

            if phrase == in1:
                points += 7

            points += phrase.count(in1)*2
            points += in1.count(phrase)


            if " " in in1:
                for word in in1.split(" "):
                    points += phrase.count(word)*2
                    

            if " " in phrase:
                for word in phrase.split(" "):
                    points += in1.count(word)
                    

            points += phrase.lower().count(in1.lower())
            points += in1.lower().count(phrase.lower())


            if " " in in1:
                for word in in1.lower().split(" "):
                    points += phrase.lower().count(word)*2
                    

            if " " in phrase:
                for word in phrase.lower().split(" "):
                    points += in1.lower().count(word)

            if points > 0:
                dist = abs(len(in1) - len(phrase))
                len_score = ((1/1.15)**(0.75*dist))*2

                points += len_score

            all_points += points
            item['ranker_points'] = points

        for item in data:
            item['score'] = item['ranker_points']/all_points

        data = sorted(data, key = lambda i: i['score'])
        data.reverse()

        return data
