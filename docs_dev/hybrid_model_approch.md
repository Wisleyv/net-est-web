Disabling the Language Model (LM) to solve the performance bottleneck is the direct cause of this poor accuracy. Let me explain exactly what was done, why it's failing academically, and propose a sound path forward.

---

### **1. What Was Done: The Shift from Semantic Analysis to Crude Pattern Matching**

To solve the timeout issue, the system's "brain" was effectively swapped out.

#### **Original Problem (The Bottleneck)**
The initial design relied on a large, powerful Language Model (`neuralmind/bert-base-portuguese-cased`, ~430MB). When analyzing text, this model had to be loaded into memory and then perform complex calculations. For a 2,292-word text, this process was exceeding the 120-second timeout because:
1.  **Model Loading:** The first time the model is used after a server start, it can take 30-60 seconds just to load into RAM.
2.  **Heavy Computation:** Comparing the semantics of numerous paragraphs is computationally expensive.

#### **The "Quick Fix" Implemented (The Root of Inaccuracy)**
To make the analysis instantaneous, I bypassed the Language Model entirely. The current strategy detection is **not using any semantic understanding**. It relies on a set of simple, non-contextual heuristic rules.

**Example of the current, flawed logic:**

*   **Before (Slow but Smart):**
    ```python
    # Compares the actual MEANING of two sentences using vectors
    similarity_score = calculate_bert_similarity(sentence1, sentence2)
    if similarity_score < 0.7:
        # High confidence of meaning change
        return "Alteração de Sentido (AS+)"
    ```

*   **After (Fast but Dumb):**
    ```python
    # Just counts how many words are identical
    word_overlap = calculate_word_overlap(sentence1, sentence2)
    if word_overlap < 0.3:
        # Assumes a meaning change with very low confidence
        return "Alteração de Sentido (AS+)"
    ```

The current system identifies strategies based on superficial characteristics like sentence counts, word lengths, and word overlap. This is why it produces nonsensical results: a short text can easily trigger multiple rules by chance, while a long, complex text might not trigger them in the same density.

---

### **2. Why This Fails Academic Standards**

An academic tool requires rigor. The current heuristic-only approach fails on multiple fronts:

1.  **High Rate of False Positives:** It identifies strategies that aren't actually present. The 99-word/4-strategy result is a classic example. A simple rephrasing might be incorrectly flagged as multiple distinct strategies.
2.  **High Rate of False Negatives:** It completely misses nuanced strategies. It cannot detect a `MOD+` (Modulação) because it doesn't understand semantics; it only sees that the words have changed.
3.  **Lack of Reproducibility and Reliability:** The results are highly sensitive to minor changes in punctuation or word choice, making them unreliable for consistent research.
4.  **No True Explainability:** The system can only explain its decision in superficial terms ("the sentence count increased"), not in linguistically meaningful ones ("the subordinate clause was transformed into a main clause to improve clarity").

---

### **3. A Sound and Solidly Grounded Approach: The Hybrid Model**

We need to re-introduce semantic intelligence without crippling the system's performance. The best practice for this scenario is a **hybrid approach** that combines a lightweight Language Model with intelligent heuristics.

**This is my strongest recommendation.**

#### **The Core Idea:**
Instead of the large 430MB BERTimbau model, we will use a much smaller, highly optimized "distilled" model. These models are designed to be about 80-90% as accurate as their larger counterparts but are 5-10 times faster and smaller.

#### **Step-by-Step Implementation Plan:**

**Step 1: Replace the Language Model**

*   **Action:** Modify the `StrategyDetector` to use a lightweight, multilingual sentence-transformer model that performs extremely well for Portuguese.
*   **Specific Model:** `paraphrase-multilingual-MiniLM-L12-v2`. This model is only ~118MB and is famously fast.
*   **Benefit:** Reduces model loading time and speeds up similarity calculations dramatically, making timeouts highly unlikely.

**Step 2: Re-architect the Heuristics as "Feature Extractors"**

*   **Action:** The heuristic rules (word counts, sentence lengths, etc.) will no longer make the final decision. Instead, they will generate a set of **features** or **evidence**.
*   **Example:**
    *   `feature_word_reduction = 0.65`
    *   `feature_sentence_split = True`
    *   `feature_semantic_similarity = 0.92` (This comes from the new, fast LLM)

**Step 3: Create an Evidence-Based Classifier**

*   **Action:** Create a final classification step that weighs the evidence from all features to make a more intelligent decision.
*   **Example Logic:**
    ```python
    # Logic for RF+ (Reescrita Global)
    if (feature_word_reduction > 0.5 and
        feature_semantic_similarity > 0.8 and
        feature_sentence_split is True):
        # Strong evidence for a global rewrite.
        return "Reescrita Global (RF+)"
    ```

**Step 4: Implement Model Caching and Pre-loading**

*   **Action:** Ensure the new, smaller model is loaded **once** when the backend server starts, not on the first user request. This eliminates the "cold start" penalty for the first user.
*   **Benefit:** All subsequent analyses will be fast, as the model is already in memory.

#### **Why This Approach is Academically Sound:**

*   **Accuracy:** It brings back the crucial semantic understanding needed to correctly identify strategies like `MOD+` and avoid the false positives of the current system.
*   **Performance:** It uses a model specifically optimized for speed, solving the timeout bottleneck.
*   **Explainability:** The system's final report can present the evidence it used for its decision (e.g., "Strategy SL+ detected with 92% confidence based on high semantic similarity and a 30% reduction in average word complexity").

This hybrid approach provides the best balance, delivering the academic rigor you require within a technically feasible and performant package suitable for hosting on services like Hugging Face.