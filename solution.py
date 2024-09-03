
from queue import PriorityQueue
class Agent(object):
    def __init__(self, phoneme_table, vocabulary) -> None:
        """
        Your agent initialization goes here. You can also add code but don't remove the existing code.
        """
        self.phoneme_table = phoneme_table
        self.vocabulary = vocabulary
        self.best_state = None
        self.best_word = None
        self.matrix =  {}
        for char in self.phoneme_table:
            for replacement in self.phoneme_table[char]:
                if(replacement not in self.matrix):
                    self.matrix[replacement] = []
                self.matrix[replacement].append(char)

    def optimize_word(self,word,idx,beam_size=3000,beam_depth=3,best_n=20,epsilon=1.05):
        self.best_word  = word
        self.best_cost = self.cost(self.current_state)
        words = self.current_state.split()
        self.wpq[idx].put((self.best_cost,self.best_word))
        self.d[idx][self.best_word] = self.best_cost
        self.initial_word = word
        f = 1+(epsilon*len(word))
        counter = 0 
        for depth in range(beam_depth):
            queue = PriorityQueue()
            new_beam = []
            for current_word in self.wbeams[idx]:
                for l in self.replacement_lens:
                    for j in range(len(current_word)):
                        if(j+l>len(current_word)): continue
                        to_replace = current_word[j:j+l]
                        if to_replace in self.matrix:
                            for replacement in self.matrix[to_replace]:
                                new_word = current_word[:j]+replacement+ current_word[j+l:]
                                words[idx] = new_word
                                new_sentence = ' '.join(words)
                                if(new_word not in self.d[idx]):
                                    c = self.cost(new_sentence)
                                    self.d[idx][new_word] = c
                                    queue.put((c,new_word))
                                    self.wpq[idx].put((c,new_word))
                                    counter +=1
            next_beam_size = 0
            while((next_beam_size< beam_size) and not queue.empty()):
                word_cost,beam_word, = queue.get()
                if(word_cost<f*self.best_cost):
                    new_beam.append(beam_word)
                    next_beam_size+=1
                    if(word_cost<self.best_cost):
                        self.best_cost = word_cost
                        self.best_word = beam_word
                else: break
            self.wbeams[idx] = new_beam
            if(counter>=100 and self.initial_word == self.best_word):
                break
        ans = []
        a = self.wpq[idx].get()
        ans.append(a[1])
        for _ in range(best_n):
            if not self.wpq[idx].empty():
                cw  = self.wpq[idx].get()
                if(a[0]*f> cw[0]):
                    ans.append(cw[1])
                else: break
            else: break
        self.best_words[idx] = ans 
        self.best_word = self.best_words[idx][0]

    def sentence_optimize(self,beam_depth,beam_size,small_beam_depth,epsilon):
        self.best_cost = self.cost(self.best_state)
        words = self.best_state.split()
        self.current_state = self.best_state
        best_words = [[] for _ in words ]
        for i,word in enumerate(words):
            self.optimize_word(word,i,beam_size = 300,beam_depth = small_beam_depth,epsilon= epsilon,best_n=10)
            words[i] = self.best_word
            self.current_state = ' '.join(words)
            self.best_state  = self.current_state
        
        current_state = self.best_state
        prq = PriorityQueue()
        for _ in range(beam_depth):
            bs_words = current_state.split(' ')
            best_cost = self.cost(current_state)
            for i, word in enumerate(bs_words):
                replacement_words = self.best_words[i]
                current_word = word
                for word1 in replacement_words:
                    bs_words[i] = word1
                    sentence_potential = ' '.join(bs_words)
                    cost_potential = self.cost(sentence_potential)
                    prq.put((-1*cost_potential,sentence_potential))
                    if(prq.qsize()>beam_size):
                        prq.get()
                    if cost_potential<best_cost:
                        best_cost = cost_potential
                        current_state = sentence_potential
                        current_word = bs_words[i]
                bs_words[i] = current_word
        self.best_state = current_state
    
    def add_words(self,k):
        current_sentence = self.best_state
        self.best_cost = self.cost(self.best_state)
        
        prq1 = PriorityQueue()
        for word in self.vocabulary:
            new_sentence = word + " " + current_sentence
            c1 = self.cost(new_sentence)
            if c1 < self.best_cost:
                self.best_state = new_sentence
                self.best_cost = c1

            prq1.put((-1*c1,word))
            if prq1.qsize() >= k:
                prq1.get()
        
        prq2 = PriorityQueue()
        for word in self.vocabulary:
            new_sentence = current_sentence  + " " + word
            c1 = self.cost(new_sentence)
            if c1 < self.best_cost:
                self.best_state = new_sentence
                self.best_cost = c1
            
            prq2.put((-1*c1,word))
            if prq2.qsize() >= k:
                prq2.get()
    
        list1 = [prq1.get()[1] for _ in range(prq1.qsize())]
        list2 = [prq2.get()[1] for _ in range(prq2.qsize())]
        
        for elem1 in list1:
            for elem2 in list2:
                new_sentence = elem1 + " " +  current_sentence + " " + elem2
                c1 = self.cost(new_sentence)
                if c1 < self.best_cost:
                    self.best_state = new_sentence
                    self.best_cost = c1
    def cost(self,text):
        return self.environment.compute_cost(text)
    def asr_corrector(self, environment):
        """
        Your ASR corrector agent goes here. Environment object has following important members.
        - environment.init_state: Initial state of the environment. This is the text that needs to be corrected.
        - environment.compute_cost: A cost function that takes a text and returns a cost. E.g., environment.compute_cost("hello") -> 0.5

        Your agent must update environment.best_state with the corrected text discovered so far.
        """
        self.environment = environment
        self.best_state = environment.init_state
        self.best_cost = self.cost(environment.init_state)
        words = self.best_state.split()
        self.beam = []
        self.wbeams =[[word] for word in words ]
        self.wpq =[PriorityQueue() for _ in words]
        self.replacement_lens = []
        self.d = [{} for _ in words]
        for rep in self.matrix:
            if(len(rep) not in self.replacement_lens):
                self.replacement_lens.append(len(rep))
        self.best_words = [None for _ in words]
        self.sentence_optimize(beam_depth=4,small_beam_depth=3,epsilon=0.020,beam_size=20)
        self.add_words(10)
            

