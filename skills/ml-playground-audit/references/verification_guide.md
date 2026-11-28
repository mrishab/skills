# Mathematical & Functional Verification Guide

This guide provides formulas, minimal verification datasets, and independent validation procedures for testing machine learning playground calculations.

---

## 1. Classification Metrics Verification

### Ground Truth Formulas
Given a binary confusion matrix:

| | Predicted Positive | Predicted Negative |
|---|---|---|
| **Actual Positive** | True Positive ($TP$) | False Negative ($FN$) |
| **Actual Negative** | False Positive ($FP$) | True Negative ($TN$) |

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

$$\text{Precision} = \frac{TP}{TP + FP} \quad (\text{Guard against } TP + FP = 0)$$

$$\text{Recall} = \frac{TP}{TP + FN} \quad (\text{Sensitivity})$$

$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN}$$

$$\text{Log Loss (Binary Cross-Entropy)} = -\frac{1}{N} \sum_{i=1}^N \left[ y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right]$$

### Minimal Verification Test Case (6 Samples)
Use this minimal test set to verify playground metric cards:
- **Actual Labels**: $Y = [1, 1, 1, 0, 0, 0]$
- **Predicted Probabilities**: $\hat{P} = [0.90, 0.80, 0.40, 0.70, 0.20, 0.10]$
- **Threshold**: $0.50 \implies \hat{Y} = [1, 1, 0, 1, 0, 0]$

**Expected Derivations**:
- $TP = 2$ (indices 0, 1)
- $FN = 1$ (index 2)
- $FP = 1$ (index 3)
- $TN = 2$ (indices 4, 5)
- $\text{Accuracy} = \frac{2 + 2}{6} = \frac{4}{6} \approx 0.6667$
- $\text{Precision} = \frac{2}{2 + 1} = \frac{2}{3} \approx 0.6667$
- $\text{Recall} = \frac{2}{2 + 1} = \frac{2}{3} \approx 0.6667$
- $F_1 = \frac{2 \cdot 2}{2 \cdot 2 + 1 + 1} = \frac{4}{6} \approx 0.6667$

**Common Failure Modes in Playgrounds**:
- Displaying training set metrics inside a card labeled "Validation Score" or "Test Score".
- F1 score crashing or showing `NaN` when $TP + FP = 0$.
- Inverting the positive/negative class convention in precision vs recall calculations.

---

## 2. Regression Metrics Verification

### Ground Truth Formulas
Given actual values $y_i$ and predicted values $\hat{y}_i$ for $i = 1, \dots, N$:

$$\text{Mean Squared Error (MSE)} = \frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2$$

$$\text{Root Mean Squared Error (RMSE)} = \sqrt{\text{MSE}}$$

$$\text{Mean Absolute Error (MAE)} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$

$$R^2 = 1 - \frac{SS_{\text{res}}}{SS_{\text{tot}}} = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

*Note: $R^2$ can be negative if the model predicts worse than the horizontal mean line $\bar{y}$. A playground that caps $R^2$ at 0 or shows 100% incorrectly is masking poor fit.*

### Minimal Verification Test Case (4 Samples)
- Actual $y = [2.0, 4.0, 5.0, 9.0]$
- Mean $\bar{y} = 5.0$
- Predictions $\hat{y} = [2.5, 3.5, 6.0, 8.0]$

**Expected Derivations**:
- Errors $e = [-0.5, 0.5, -1.0, 1.0]$
- Squared Errors $e^2 = [0.25, 0.25, 1.0, 1.0] \implies \sum e^2 = 2.50$
- Absolute Errors $|e| = [0.5, 0.5, 1.0, 1.0] \implies \sum |e| = 3.00$
- $SS_{\text{tot}} = (2-5)^2 + (4-5)^2 + (5-5)^2 + (9-5)^2 = 9 + 1 + 0 + 16 = 26.0$
- $\text{MSE} = \frac{2.5}{4} = 0.625$
- $\text{RMSE} = \sqrt{0.625} \approx 0.7906$
- $\text{MAE} = \frac{3.0}{4} = 0.75$
- $R^2 = 1 - \frac{2.5}{26.0} = 1 - 0.09615 \approx 0.9038$

---

## 3. Clustering & Unsupervised Verification

### K-Means Inertia (Within-Cluster Sum of Squares - WCSS)
$$\text{WCSS} = \sum_{k=1}^K \sum_{x \in C_k} \| x - \mu_k \|^2$$

### Verification Check:
- For $K=1$, centroid $\mu = \frac{1}{N}\sum x_i$. WCSS equals total dataset variance $\times N$.
- For $K=N$, each point is its own centroid $\implies \text{WCSS} \equiv 0$.
- If $K=N$ does not yield 0 inertia, the calculation is defective.

---

## 4. Geometric & Visualization Integrity Verification

### 1. Aspect Ratio & Distance Distortion
- **The Issue**: Algorithms relying on Euclidean distance ($d = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$) require an isotropic (1:1) coordinate system.
- **The Defect**: If the canvas viewport stretches the X-axis (e.g. 800px wide for range $[0, 1]$) compared to the Y-axis (e.g. 400px high for range $[0, 1]$), circles appear as ellipses.
- **Visual Verification**: Place 3 equidistant points forming an equilateral triangle. If the rendered decision boundary or cluster boundary is not symmetric, the visualization code is using unscaled screen pixels rather than normalized data coordinates.

### 2. Decision Boundary Resolution
- **The Issue**: Client-side playgrounds typically evaluate model predictions over a 2D grid (e.g., $50 \times 50$ or $100 \times 100$ cells) and render a contour or heatmap.
- **Artifacts to Check**:
  - Jagged staircasing caused by low grid sampling.
  - Off-by-one pixel shifts between points and the boundary background.
  - Inverted class color mappings (e.g., points of class A plotted inside region colored for class B).

---

## 5. State Staleness Verification Protocol

Follow this exact test sequence to detect silent state desynchronization:

1. **Step 1**: Train model on Dataset A with parameter $P = 1.0$. Note the displayed Accuracy and visual fit.
2. **Step 2**: Change parameter to $P = 5.0$ *without* clicking "Train" or "Run".
   - *Expected*: Either the interface automatically recomputes, or an explicit badge/banner indicates "Stale Results / Retrain Required".
   - *Failure*: Playground shows old metrics alongside new parameter configuration without indicating staleness.
3. **Step 3**: Add 5 new data points via canvas clicking.
   - *Expected*: Boundary either resets or indicates data change.
   - *Failure*: Points render on canvas, but metric cards still show pre-edit sample count and accuracy.
