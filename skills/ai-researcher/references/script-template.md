# 60-Second Video Script Template (150-180 words)

**Language & Tone Constraints:**
- **Spoken, Not Written:** Write exactly how a person speaks. Do NOT write like a textbook, abstract, or research paper.
- **Common Tongue:** Use simple, everyday vocabulary for the connective tissue of the sentences. 
- **Technical but Accessible:** Keep the deep technical terms (e.g., "Jacobian", "manifolds", "O(n²)") but explain the actions happening to them using simple verbs (e.g., "bending", "shrinking", "throwing away" instead of "transforming", "attenuating", "discarding").

This template ensures maximum density and intuition, matching a 3blue1brown-style geometric explanation.

**[0:00 - 0:10] The Hook (High-Retention Pattern Break)**
DO NOT use slow, historical preambles like "For decades...". Jump immediately into a pattern-breaking, high-retention hook engineered for scroll-stopping engagement. Use one of these proven frameworks adapted for an elite technical audience:
- **The Paradigm Inversion:** "Stop thinking about [Concept] as [Standard View]. This new paper proves it's actually [New Mathematical View]."
- **The Fatal Flaw:** "The way we currently calculate [X] is fundamentally broken. Here is how [Authors/Lab] just fixed it."
- **The Extreme Result:** "This new paper just cut [Cost/Memory/Time] by [X]% without scaling up the architecture, using one brilliant math trick."
- **The Direct Tradeoff:** "Give me 60 seconds to explain the precise math behind the paper that just broke [Benchmark/Limit]."
- **The Contrarian:** "Everyone is obsessing over [Hype Topic], but the real breakthrough is buried in this paper's [Math Concept]."
- **The Hidden Mechanism:** "You know how [Model] does [Task]? You probably think it's doing [Assumption], but mathematically, it's actually doing [Surprising Reality]."

*Example: "Stop thinking about neural network layers as discrete mathematical steps. This new paper proves you can model them as a continuous differential equation..."*

**[0:10 - 0:40] The Geometric Intuition (The Meat)**
Explain the math visually. Use terms involving vectors, matrices, manifolds, and projections.
*Example: "Imagine the attention matrix not as a grid, but as a routing network. Instead of computing the entire O(n^2) space, they project the vectors onto a lower-dimensional manifold..."*

**[0:40 - 0:50] The Prerequisite Bridge**
Briefly anchor the concept to foundational math.
*Example: "This works because of the Eckart-Young theorem for SVD, which guarantees this is the optimal low-rank approximation."*

**[0:50 - 0:60] The Impact (The Payoff)**
State the concrete technical result.
*Example: "By doing this, they drop memory usage by 80% with zero loss in accuracy. The math is brilliant, and the code is open-source."*

## Visual Prompts & Manim Code
For each section, include:
1.  A `[Visual Action]` tag describing the animation (e.g., `[Visual: A 3D plane morphing into a saddle point]`).
2.  **[Optional]** A `[Manim Snippet]` block containing Python code for the `Manim` Mathematical Animation Engine. Focus on the core geometric transformation.

*Example:*
```python
# [Manim Snippet: Manifold Projection]
class Projection(Scene):
    def construct(self):
        plane = NumberPlane()
        self.play(Create(plane))
        # ... transformation logic
```