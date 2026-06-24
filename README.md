# 🧬 GeneQuantify: Advanced qPCR Expression Analysis

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg.svg)](https://genequantify.streamlit.app/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

[Türkçe](#türkçe) | [English](#english)

---

<a name="english"></a>
## 🇺🇸 English

**GeneQuantify** is a high-precision, open-source platform for qPCR gene expression analysis. It automates the full workflow — from raw Cq values to statistically validated results — following MIQE guidelines (Bustin et al., 2009).

### 🚀 Getting Started

1. Upload your data at [genequantify.streamlit.app](https://genequantify.streamlit.app/)
2. Define your control group and reference genes
3. Run the analysis and download results as CSV or PDF

### 🛠️ Local Installation

```bash
git clone https://github.com/burhanettiny/GeneQuantify.git
cd GeneQuantify
pip install -r requirements.txt
streamlit run app.py
```

**Requirements:** Python ≥ 3.9, see `requirements.txt` for full list.

---

## 📐 Mathematical Formulas

### 1. Normalization Factor (NF)

For a single reference gene:

```
NF_sample = Cq_ref
```

For multiple reference genes (geNorm approach, Vandesompele et al. 2002):

```
NF_sample = mean(Cq_ref1, Cq_ref2, ..., Cq_refN)
```

This arithmetic mean of Cq values corresponds to the geometric mean of expression levels on the linear scale, as recommended by the MIQE guidelines.

### 2. Delta Cq (ΔCq)

```
ΔCq_sample = Cq_target - NF_sample
```

Computed per replicate before averaging.

### 3. Classic ΔΔCq Method (Livak & Schmittgen, 2001)

```
ΔCq_control    = mean(ΔCq values of control group)
ΔCq_sample     = mean(ΔCq values of patient/treatment group)

ΔΔCq           = ΔCq_sample − ΔCq_control

Fold Change    = 2^(−ΔΔCq)
```

**Assumption:** Equal amplification efficiency for target and reference genes (E ≈ 2.0, i.e., 100%). Valid when efficiency difference < 10%.

### 4. Pfaffl Method (Pfaffl, 2001)

```
ΔCq_target = Cq_target_control − Cq_target_sample
ΔCq_ref    = Cq_ref_control    − Cq_ref_sample

Ratio (Pfaffl) = (E_target ^ ΔCq_target) / (E_ref ^ ΔCq_ref)
```

Where `E_target` and `E_ref` are the primer-specific amplification efficiencies (E = 2.0 corresponds to 100%). **Recommended when efficiency difference > 10%.**

### 5. Relative Quantity (RQ)

```
RQ = 2^(−ΔCq)
```

All statistical tests are performed on RQ values, not raw ΔCq. This is because ΔCq is on a logarithmic scale, and applying parametric tests (e.g., t-test) directly to ΔCq can underestimate biological variability and increase false positives.

### 6. Regulation Thresholds

| Fold Change    | ΔΔCq Range    | Classification            |
|----------------|---------------|---------------------------|
| ≥ 2.0          | < −1.0        | Strong upregulation       |
| 1.5 – 2.0      | −1.0 to −0.58 | Moderate upregulation     |
| 1.0 – 1.5      | −0.58 to 0    | Weak upregulation         |
| ≈ 1.0          | ≈ 0           | No change                 |
| 0.67 – 1.0     | 0 to 0.58     | Weak downregulation       |
| 0.5 – 0.67     | 0.58 to 1.0   | Moderate downregulation   |
| < 0.5          | > 1.0         | Strong downregulation     |

The 1.5/0.67 threshold (equivalent to ±0.58 ΔΔCq) is widely used in the qPCR literature as a biologically meaningful cutoff.

---

## 🔬 Reference Gene Stability (geNorm M-value)

**geNorm M-value** quantifies the expression stability of each reference gene relative to the others (Vandesompele et al., 2002):

```
For each reference gene r:
  M_r = mean over all other reference genes s of: SD(log2(Cq_r / Cq_s))
```

Lower M = more stable. Thresholds:
- M < 0.5 → Stable (MIQE strict threshold)
- 0.5 ≤ M < 1.0 → Borderline (MIQE acceptable)
- M ≥ 1.0 → Unstable — use with caution

**Coefficient of Variation (CV):**

```
CV (%) = (SD / mean) × 100
```

Computed on raw Cq values across all samples. CV < 5% indicates low technical variability.

---

## 📊 Automated Statistical Decision Tree

All statistical tests are performed on **RQ values (2^−ΔCq)**. The test is selected automatically using a sequential decision procedure:

### Step 1 — Check sample size
```
If n_control < 2 OR n_group < 2:
    → No statistical test (insufficient data)
```

### Step 2 — Normality test (Shapiro-Wilk)
```
Minimum n required: 8 (per group)

If n ≥ 8 (both groups):
    Apply Shapiro-Wilk to RQ values of each group
    normal = True  if  p_shapiro > 0.05

If n < 8 (either group):
    Shapiro-Wilk is skipped (unreliable at small n)
    normal = True  (parametric test assumed)
```

**Justification:** The Shapiro-Wilk test has low power for n < 8 and can fail to detect non-normality in small samples. Defaulting to parametric tests at n < 8 follows standard practice in small-sample molecular biology studies.

### Step 3 — Variance homogeneity test (Levene's test)
```
Performed only if both groups are normal

levene_p = Levene's test p-value
equal_variance = True  if  levene_p > 0.05
```

### Step 4 — Test selection
```
If control_normal AND sample_normal:
    If equal_variance:
        → Student's t-test (two-sided, independent samples)
          scipy: ttest_ind(control_rq, sample_rq)
    Else:
        → Welch's t-test (two-sided, unequal variances)
          scipy: ttest_ind(control_rq, sample_rq, equal_var=False)
Else (any group non-normal):
    → Mann-Whitney U test (two-sided, non-parametric)
      scipy: mannwhitneyu(control_rq, sample_rq, alternative='two-sided')

Significance threshold: p < 0.05
```

### Decision Tree Diagram

```
RQ values (2^-ΔCq)
        │
        ▼
  n ≥ 2 per group?
  ├─ No  → No test (N/A)
  └─ Yes ▼
        │
  n ≥ 8 per group?
  ├─ No  → Skip Shapiro-Wilk, assume normal
  └─ Yes → Shapiro-Wilk (α = 0.05)
        │
  Both groups normal?
  ├─ No  → Mann-Whitney U (non-parametric)
  └─ Yes → Levene's test (α = 0.05)
                │
        Equal variances?
        ├─ Yes → Student's t-test
        └─ No  → Welch's t-test
```

---

## 📊 Multi-group Analysis (≥ 3 groups)

When ≥ 3 groups are present, an omnibus test is applied before pairwise comparisons to control Type I error:

```
All groups normal AND equal variances:
    → One-way ANOVA → post-hoc: Tukey HSD

All groups normal AND unequal variances:
    → Welch ANOVA (Alexander-Govern) → post-hoc: Games-Howell

Any group non-normal:
    → Kruskal-Wallis → post-hoc: Dunn (Mann-Whitney U pairwise)
```

**Multiple comparison correction (post-hoc):**
- **Bonferroni** — controls family-wise error rate (FWER). Conservative; best for few comparisons.
- **FDR (Benjamini-Hochberg, 1995)** — controls false discovery rate. Recommended for many comparisons.

Both corrections are reported simultaneously.

---

## 🔍 Outlier Detection

### Grubbs Test (Grubbs, 1969)
```
G = |x_suspect − mean(x)| / SD(x)

Critical value G_crit derived from t-distribution:
    t_crit = t(α/(2N), N−2)
    G_crit = ((N−1) / √N) × √(t_crit² / (N−2 + t_crit²))

Outlier if G > G_crit  (p < α)
```
Assumes normality. Minimum n = 3. Applied iteratively until no further outliers are detected.

### IQR Method (Tukey, 1977)
```
IQR = Q3 − Q1
Lower bound = Q1 − k × IQR
Upper bound = Q3 + k × IQR

Default k = 1.5 (standard); user-adjustable to 3.0 (conservative)
```
Non-parametric. Recommended for larger groups or non-normal distributions.

**Important:** Outlier exclusion is not automatic. Flagged values are shown to the user for manual confirmation. All exclusions are logged in the output table and PDF report.

---

## 📈 Amplification Efficiency

```
From standard curve slope:
    E = 10^(−1 / slope)

Accepted range: E = 1.8–2.2  (90–110%)

Efficiency difference threshold (default 10%, per MIQE):
    If |E_target − E_ref| / E_ref × 100 > threshold:
        → Pfaffl method recommended over classic ΔΔCq
```

---

## 🌐 Supported Languages

The interface and PDF reports are available in 6 languages: English, Turkish, German, French, Spanish, Arabic. Translation quality is maintained by the developer; scientific terminology follows standard nomenclature in each language.

---

## 📚 References

1. Livak KJ & Schmittgen TD (2001). Analysis of relative gene expression data using real-time quantitative PCR and the 2−ΔΔCT method. *Methods*, 25(4), 402–408.
2. Pfaffl MW (2001). A new mathematical model for relative quantification in real-time RT-PCR. *Nucleic Acids Research*, 29(9), e45.
3. Vandesompele J et al. (2002). Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes. *Genome Biology*, 3(7), research0034.
4. Bustin SA et al. (2009). The MIQE guidelines: minimum information for publication of quantitative real-time PCR experiments. *Clinical Chemistry*, 55(4), 611–622.
5. Grubbs FE (1969). Procedures for detecting outlying observations in samples. *Technometrics*, 11(1), 1–21.
6. Tukey JW (1977). *Exploratory Data Analysis*. Addison-Wesley.
7. Benjamini Y & Hochberg Y (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society B*, 57(1), 289–300.

---

## ⚖️ License & Contact

- License: [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0)
- Developer: Burhanettin Yalçınkaya
- Contact: [mailtoburhanettin@gmail.com](mailto:mailtoburhanettin@gmail.com)
- For research and educational use only. Not validated for clinical diagnosis.

---

<a name="türkçe"></a>
## 🇹🇷 Türkçe

**GeneQuantify**, moleküler biyoloji araştırmalarında qPCR verilerinin analizi için geliştirilmiş açık kaynaklı, yüksek hassasiyetli bir platformdur. Ham Cq değerlerinden istatistiksel sonuçlara kadar tüm süreci MIQE kılavuzlarına (Bustin et al., 2009) uygun şekilde otomatikleştirir.

### 🚀 Kullanım

1. Verilerinizi [genequantify.streamlit.app](https://genequantify.streamlit.app/) üzerinden yükleyin.
2. Kontrol grubunuzu ve referans geninizi seçin.
3. Analizi başlatın ve sonuçları CSV veya PDF olarak indirin.

### 🛠️ Kurulum

```bash
git clone https://github.com/burhanettiny/GeneQuantify.git
cd GeneQuantify
pip install -r requirements.txt
streamlit run app.py
```

---

## 📐 Matematiksel Formüller

### 1. Normalizasyon Faktörü (NF)

Tek referans gen:
```
NF_örnek = Cq_ref
```

Çoklu referans gen (geNorm yaklaşımı, Vandesompele et al. 2002):
```
NF_örnek = ortalama(Cq_ref1, Cq_ref2, ..., Cq_refN)
```

### 2. Delta Cq (ΔCq)

```
ΔCq_örnek = Cq_hedef − NF_örnek
```

### 3. Klasik ΔΔCq Yöntemi (Livak & Schmittgen, 2001)

```
ΔCq_kontrol  = ortalama(kontrol grubu ΔCq değerleri)
ΔCq_örnek    = ortalama(hasta/tedavi grubu ΔCq değerleri)

ΔΔCq         = ΔCq_örnek − ΔCq_kontrol

Kat Değişimi = 2^(−ΔΔCq)
```

### 4. Pfaffl Yöntemi (Pfaffl, 2001)

```
ΔCq_hedef  = Cq_hedef_kontrol − Cq_hedef_örnek
ΔCq_ref    = Cq_ref_kontrol   − Cq_ref_örnek

Oran (Pfaffl) = (E_hedef ^ ΔCq_hedef) / (E_ref ^ ΔCq_ref)
```

### 5. Göreli Miktar (RQ)

```
RQ = 2^(−ΔCq)
```

Tüm istatistiksel testler RQ değerleri üzerinden uygulanır. ΔCq değerleri logaritmik ölçekte olduğundan, doğrudan ΔCq üzerinden t-testi biyolojik değişkenliği hafife alabilir.

---

## 📊 Otomatik İstatistiksel Karar Ağacı

### Adım 1 — Örneklem büyüklüğü kontrolü
```
n_kontrol < 2 VEYA n_grup < 2 ise → Test uygulanamaz
```

### Adım 2 — Normallik testi (Shapiro-Wilk)
```
Minimum n: 8 (her grup için)

n ≥ 8 ise: Shapiro-Wilk uygulanır (p > 0.05 → normal)
n < 8 ise: Shapiro-Wilk atlanır; parametrik test varsayılır
```

**Gerekçe:** n < 8'de Shapiro-Wilk düşük güce sahiptir; küçük örneklemlerde normallikten sapmayı tespit etmekte güvenilir değildir.

### Adım 3 — Varyans homojenliği (Levene testi)
```
Yalnızca her iki grup normal dağılımlıysa uygulanır.
levene_p > 0.05 → eşit varyans
```

### Adım 4 — Test seçimi
```
Her iki grup normal:
    Eşit varyans → Student t-testi
    Eşit olmayan varyans → Welch t-testi
Herhangi bir grup normal değil → Mann-Whitney U testi

Anlamlılık eşiği: p < 0.05
```

### Karar Ağacı

```
RQ değerleri (2^-ΔCq)
        │
        ▼
  Her grupta n ≥ 2?
  ├─ Hayır → Test yok (N/A)
  └─ Evet  ▼
        │
  Her grupta n ≥ 8?
  ├─ Hayır → Shapiro-Wilk atlanır, normallik varsayılır
  └─ Evet  → Shapiro-Wilk (α = 0.05)
        │
  Her iki grup normal mi?
  ├─ Hayır → Mann-Whitney U (parametrik olmayan)
  └─ Evet  → Levene testi (α = 0.05)
                │
        Eşit varyans?
        ├─ Evet → Student t-testi
        └─ Hayır → Welch t-testi
```

---

## 📚 Kaynaklar

1. Livak KJ & Schmittgen TD (2001). *Methods*, 25(4), 402–408.
2. Pfaffl MW (2001). *Nucleic Acids Research*, 29(9), e45.
3. Vandesompele J et al. (2002). *Genome Biology*, 3(7), research0034.
4. Bustin SA et al. (2009). *Clinical Chemistry*, 55(4), 611–622.
5. Grubbs FE (1969). *Technometrics*, 11(1), 1–21.
6. Tukey JW (1977). *Exploratory Data Analysis*. Addison-Wesley.
7. Benjamini Y & Hochberg Y (1995). *J R Stat Soc B*, 57(1), 289–300.

---

**Lisans:** GPL-3.0 | **Geliştirici:** Burhanettin Yalçınkaya | **İletişim:** mailtoburhanettin@gmail.com  
*Yalnızca araştırma ve eğitim amaçlıdır. Klinik tanı için doğrulanmamıştır.*
