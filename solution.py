from queue import PriorityQueue

class Agent(object):
    def __init__(self, phoneme_table, vocabulary) -> None:
        """
        Your agent initialization goes here. You can also add code but don't remove the existing code.
        """
        self.phoneme_table = phoneme_table
        self.vocabulary = vocabulary
        self.best_state = None
        self.inverse_vocab = {}
        for char in self.vocabulary:
            for replacement_char in self.vocabulary[char]:
                if replacement_char not in self.inverse_vocab:
                    self.inverse_vocab[replacement_char] = []
                self.inverse_vocab[replacement_char].append(char)

    def optimize_word(self, word, word_idx, beam_size=30000, beam_depth=1, best_n=20, epsilon=1.05):
        self.best_word = word
        self.best_word_cost = self.environment.compute_cost(self.best_word)

        self.bwq[word_idx].put((self.best_word_cost, self.best_word))
        self.d[word_idx][self.best_word] = self.best_word_cost
        words = self.current_state.split()

        lw = len(word)
        f = 1 + (epsilon * lw)
        for depth in range(beam_depth):
            queue = PriorityQueue()
            new_beam = []

            for current_solution in self.wbeams[word_idx]:
                for char_idx in range(len(word)):
                    if current_solution[char_idx] in self.phoneme_table:
                        for replace_current_char in self.phoneme_table[current_solution[char_idx]]:
                            new_word = current_solution[:char_idx] + replace_current_char + current_solution[char_idx+1:]
                            words[word_idx] = new_word
                            new_string = ' '.join(words)
                            if new_word not in self.d[word_idx]:
                                ft = self.environment.compute_cost(new_string)
                                self.d[word_idx][new_word] = ft
                                queue.put((ft, new_word))
                                self.bwq[word_idx].put((ft, new_word))

            next_beam_size = 0
            while next_beam_size < beam_size and not queue.empty():
                best_word_tuple = queue.get()
                if best_word_tuple[0] < f * self.best_cost:
                    new_beam.append(best_word_tuple[1])
                    next_beam_size += 1
                    if best_word_tuple[0] < self.best_cost:
                        self.best_cost = best_word_tuple[0]
                        self.best_word = best_word_tuple[1]
                else:
                    break
            self.wbeams[word_idx] = new_beam

        ans = []
        u = []
        if not self.bwq[word_idx].empty():
            a = self.bwq[word_idx].get()
            ans.append(a[1])
            u.append(a)

            for _ in range(best_n-1):
                if not self.bwq[word_idx].empty():
                    t = self.bwq[word_idx].get()
                    if a[0] * 1.15 > t[0]:
                        ans.append(t[1])
                        u.append(t)
                    else:
                        break
                else:
                    break

        self.best_words[word_idx] = ans

    def per_word_optimization(self, start_state, beam_size=40, beam_depth=5, small_beam_depth=3, epsilon=1.05):
        self.best_state = start_state
        self.best_cost = self.environment.compute_cost(self.best_state)
        self.current_state = self.best_state
        words = start_state.split()
        self.best_words = [[] for _ in words]

        for word_idx, word in enumerate(words):
            self.optimize_word(word, word_idx, beam_depth=small_beam_depth, epsilon=epsilon)
            optimized_word = self.best_word
            words[word_idx] = optimized_word
            self.current_state = ' '.join(words)
            self.best_state = self.current_state

        if len(self.beam) == 0:
            self.beam = [self.best_state]

        for _ in range(beam_depth):
            prq = PriorityQueue()
            for cs in self.beam:
                cs_words = cs.split(' ')
                for i, word in enumerate(cs_words):
                    for pos_rep in self.best_words[i]:
                        new_sol = ' '.join(cs_words[:i] + [pos_rep] + cs_words[i+1:])
                        cost = self.environment.compute_cost(new_sol)
                        prq.put((cost, new_sol))
            next_beam = []
            for _ in range(beam_size):
                if prq.empty():
                    break
                possol = prq.get()
                next_beam.append(possol[1])
                if possol[0] < self.environment.compute_cost(self.best_state):
                    self.best_cost = possol[0]
                    self.best_state = possol[1]
            self.beam = next_beam

    def asr_corrector(self, environment):
        """
        Your ASR corrector agent goes here. Environment object has following important members.
        - environment.init_state: Initial state of the environment. This is the text that needs to be corrected.
        - environment.compute_cost: A cost function that takes a text and returns a cost. E.g., environment.compute_cost("hello") -> 0.5

        Your agent must update environment.best_state with the corrected text discovered so far.
        """
        self.best_state = environment.init_state
        cost = environment.compute_cost(environment.init_state)
        self.environment = environment
        words = environment.init_state.split()

        self.beam = []
        self.wbeams = [[word] for word in words]
        self.d = [{} for _ in words]
        self.bwq = [PriorityQueue() for _ in words]

        self.per_word_optimization(start_state=environment.init_state, beam_depth=4, small_beam_depth=1, epsilon=0.035)
        self.per_word_optimization(start_state=self.best_state, small_beam_depth=1, epsilon=0.005)

        environment.best_state = self.best_state
        print(f"Final corrected state: {self.best_state}, with cost: {self.best_cost}")
