# Correction Agent for ASR Errors

## Authors
- Anup Lal Nayak: 2022CS51827
- Abhishek Amrendra Kumar: 2022CS11598

## Overview
This project involves building an agent to correct errors in text generated by Automatic Speech Recognition (ASR) systems. These errors typically include incorrect character recognition and missing words at the start or end of a sentence.

The agent refines the text to closely match the intended spoken input using a search-based method, specifically **local search**. 

### Why Local Search?
- **Uninformed Search** methods like Depth-First Search (DFS) and Breadth-First Search (BFS) are inefficient due to exponential growth in corrections for longer sentences.
- **Informed Search** methods, such as A*, require a clear goal state and an effective heuristic, which are difficult to define in the ASR correction task.

Local Search is better suited for this problem because it focuses on iteratively improving a single solution by exploring neighboring states. It efficiently navigates the search space to find low-cost corrections, making it scalable and adaptable to complex ASR tasks.

## Core Approach
The agent is built around a **beam search technique** enhanced by local optimizations.

### Key Steps:
1. **Initialization**:  
   The agent loads a phoneme table and vocabulary to recognize possible substitutions for characters and potential missing words.
   
2. **Word-Level Optimization**:  
   The `optimize_word` function generates possible word substitutions based on the phoneme table. These substitutions are evaluated based on cost, and the best candidates are retained.

3. **Sentence-Level Optimization**:  
   The `sentence_optimize` function applies beam search to optimize the entire sentence. Candidate sentences are iteratively improved by substituting words with better alternatives from the word-level optimization phase.

4. **Add-Words**:  
   The agent identifies the top `k` prefix and suffix words based on their costs when added to the best sentence. It explores all combinations of these prefixes and suffixes with the top `n` candidate sentences, selecting the sentence with the lowest cost as the best state.

## Data Structures and Search Strategy
- **UniquePriorityQueue**:  
   A hybrid of Set and Priority Queue data structures is used to manage and retrieve the best candidate words and sentences efficiently. This ensures that the beam search remains focused on the most promising candidates while avoiding duplicates.

- **Heuristic Function**:  
   The cost function evaluates the likelihood of a sentence matching the original audio. Lower costs indicate better corrections.

## Optimizations
1. **Beam Search Optimization**:
   - **Adaptive Beam Length**:  
     The beam length is dynamically adjusted based on the search depth and progress, balancing exploration and exploitation.
   - **Early Stopping**:  
     The algorithm stops if no improvement is made after a certain number of iterations.

2. **Word Prioritization**:  
   More critical or promising words are prioritized based on their impact on the overall cost during sentence optimization.

3. **Multiple Beam Resolutions**:  
   The agent applies different beam resolutions for word-level and sentence-level optimizations. Sentence-level optimizations use a broader beam, while word-level uses a more focused one.

## Complexity Considerations
- **Branching Factor Control**:  
   By controlling the number of candidates in the beam and prioritizing based on cost, the agent manages the branching factor effectively, keeping the search computationally feasible even for long sentences.

- **Cost Function Independence**:  
   The implementation is agnostic of the specific cost function used, making it flexible to different evaluation metrics during testing.

## Conclusion
This correction agent combines beam search, local optimization, and efficient data management through priority queues to correct ASR errors. It is designed to handle complex errors in ASR-generated text while ensuring computational efficiency. The approach is flexible enough to adapt to different error types and sentence structures, achieving high accuracy within time constraints.
