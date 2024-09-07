class UniquePriorityQueue:
    def __init__(self):
        self.heap = []  # To store the heap elements
        self.entry_finder = {}  # Dictionary to ensure elements are unique

    def push(self, priority, item):
        if item in self.entry_finder:
            return  # Do not insert duplicates
        self.entry_finder[item] = priority
        self.heap.append((priority, item))
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            raise KeyError('pop from an empty priority queue')
        # Swap the first item with the last one and remove the last item
        self._swap(0, len(self.heap) - 1)
        priority, item = self.heap.pop()
        del self.entry_finder[item]
        self._sift_down(0)
        return priority,item

    def _sift_up(self, idx):
        parent = (idx - 1) // 2
        if idx > 0 and self.heap[idx][0] < self.heap[parent][0]:
            self._swap(idx, parent)
            self._sift_up(parent)

    def _sift_down(self, idx):
        child = 2 * idx + 1
        if child < len(self.heap):
            # Check if the right child exists and is smaller
            if child + 1 < len(self.heap) and self.heap[child + 1][0] < self.heap[child][0]:
                child += 1
            if self.heap[child][0] < self.heap[idx][0]:
                self._swap(idx, child)
                self._sift_down(child)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def __len__(self):
        return len(self.entry_finder)
    
    def isEmpty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)
    
    
class Agent(object):
    def __init__(self, phoneme_table, vocabulary) -> None:
        """
        Your agent initialization goes here. You can also add code but don't remove the existing code.
        """
        self.phoneme_table = phoneme_table
        self.vocabulary = vocabulary
        self.best_state = None
        self.bestWord = None
        self.lookupTable =  {}
        for char in self.phoneme_table:
            for replacement in self.phoneme_table[char]:
                if(replacement not in self.lookupTable):
                    self.lookupTable[replacement] = []
                self.lookupTable[replacement].append(char)

    def optimize_word(self,word,idx,beamLength=3000,beamDepth=3,best_n=20,v=1.05):
        self.bestWord  = word
        self.best_cost = self.cost(self.currentState)
        words = self.currentState.split()
        self.wordPQ[idx].push(self.best_cost,self.bestWord)
        self.d[idx][self.bestWord] = self.best_cost
        self.initialWord = word
        f = 1+(v*len(word))
        counter = 0 
        for depth in range(beamDepth):
            queue = UniquePriorityQueue()
            new_beam = []
            for current_word in self.beamWord[idx]:
                for l in self.replacementLens:
                    for j in range(len(current_word)):
                        if(j+l>len(current_word)): continue
                        to_replace = current_word[j:j+l]
                        if to_replace in self.lookupTable:
                            for replacement in self.lookupTable[to_replace]:
                                new_word = current_word[:j]+replacement+ current_word[j+l:]
                                words[idx] = new_word
                                newSentence = ' '.join(words)
                                if(new_word not in self.d[idx]):
                                    c = self.cost(newSentence)
                                    self.d[idx][new_word] = c
                                    queue.push(c,new_word)
                                    self.wordPQ[idx].push(c,new_word)
                                    counter +=1
            next_BeamLength = 0
            while((next_BeamLength< beamLength) and not queue.isEmpty()):
                word_cost,beam_word = queue.pop()
                if(word_cost<f*self.best_cost):
                    new_beam.append(beam_word)
                    next_BeamLength+=1
                    if(word_cost<self.best_cost):
                        self.best_cost = word_cost
                        self.bestWord = beam_word
                else: break
            self.beamWord[idx] = new_beam
            if(counter>=100 and self.initialWord == self.bestWord):
                break
        ans = []
        a = self.wordPQ[idx].pop()
        ans.append(a[1])
        for _ in range(best_n):
            if not self.wordPQ[idx].isEmpty():
                cw  = self.wordPQ[idx].pop()
                ans.append(cw[1])
            else: break
        self.bestWords[idx] = ans 
        self.bestWord = self.bestWords[idx][0]

    def sentence_optimize(self,beamDepth,beamLength,smallBeamDepth,v):
        self.best_cost = self.cost(self.best_state)
        words = self.best_state.split()
        self.currentState = self.best_state
        bestWords = [[] for _ in words ]
        for i,word in enumerate(words):
            self.optimize_word(word,i,beamLength = 300,beamDepth = smallBeamDepth,v= v,best_n=7)
            words[i] = self.bestWord
            self.currentState = ' '.join(words)
            self.best_state  = self.currentState
        
        currentState = self.best_state
        prq = UniquePriorityQueue()
        for _ in range(beamDepth):
            bestSentenceWords = currentState.split(' ')
            best_cost = self.cost(currentState)
            for i, word in enumerate(bestSentenceWords):
                replacement_words = self.bestWords[i]
                current_word = word
                for word1 in replacement_words:
                    bestSentenceWords[i] = word1
                    SentencePotential = ' '.join(bestSentenceWords)
                    cost_potential = self.cost(SentencePotential)
                    prq.push(-1*cost_potential,SentencePotential)
                    if(prq.size()>beamLength):
                        prq.pop()
                    if cost_potential<best_cost:
                        best_cost = cost_potential
                        currentState = SentencePotential
                        current_word = bestSentenceWords[i]
                bestSentenceWords[i] = current_word
        self.best_state = currentState
        self.best_cost = best_cost

        while(prq.size()>4):
            prq.pop()
        while(prq.size()):
            s = prq.pop()[1]
            self.bestSentences.append(s)
    def optimize(self,k):
        prq1 = UniquePriorityQueue()
        for word in self.vocabulary:
            newSentence = word + " " + self.best_state
            c1 = self.cost(newSentence)
            prq1.push(-1*c1,word)
            if prq1.size() >= k:
                prq1.pop()
        
        prq2 = UniquePriorityQueue()
        for word in self.vocabulary:
            newSentence = self.best_state  + " " + word
            c1 = self.cost(newSentence)
            prq2.push(-1*c1,word)
            if prq2.size() >= k:
                prq2.pop()
    
        l1 = [prq1.pop()[1] for _ in range(prq1.size())]
        l2 = [prq2.pop()[1] for _ in range(prq2.size())]
        l1.append("")
        l2.append("")
        return l1,l2
    def add_words(self,list1,list2):
        current_sentence = self.tempState
        for elem1 in list1:
            for elem2 in list2:
                newSentence = current_sentence
                if(elem1!=""):
                    newSentence = elem1 +" "+newSentence
                if(elem2!=""):
                    newSentence = newSentence+" "+elem2
                c1 = self.cost(newSentence)
                if c1 < self.best_cost:
                    self.best_state = newSentence
                    self.best_cost = c1
                    
                    
    def cost(self,text):
        return self.environment.compute_cost(text)
    def asr_corrector(self, environment):
        """
        Your ASR corrector agent goes here. Environment object has following important members.
        - environment.init_state: Initial state of the environment. This is the text that needs to be corrected.
        - environment.compushe_cost: A cost function that takes a text and returns a cost. E.g., environment.compushe_cost("hello") -> 0.5

        Your agent must update environment.best_state with the corrected text discovered so far.
        """
        self.environment = environment
        self.best_state = environment.init_state
        self.best_cost = self.cost(environment.init_state)
        self.bestSentences = []
        self.tempState = environment.init_state
        words = self.best_state.split()
        self.beam = []
        self.beamWord =[[word] for word in words ]
        self.wordPQ =[UniquePriorityQueue() for _ in words]
        self.replacementLens = [1,2]
        self.d = [{} for _ in words]
        self.bestWords = [None for _ in words]
        self.sentence_optimize(beamDepth=4,smallBeamDepth=3,v=0.020,beamLength=20)
        list1,list2 = self.optimize(5)
        for sentence in self.bestSentences:
            self.tempState = sentence
            self.add_words(list1,list2)