import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import scipy.stats as stats
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import pdfbase
from reportlab.pdfbase import pdfmetrics
import plotly.io as pio
import matplotlib.pyplot as plt
from reportlab.lib import colors
import streamlit.components.v1 as components
import os
import urllib.request
import glob



st.set_page_config(page_title="GeneQuantify", layout="wide")

if 'language' not in st.session_state:
    st.session_state.language = "English" 


if 'language' not in st.session_state:
    st.session_state.language = "English" 
    

flags = {
    "Türkçe": "🇹🇷",
    "English": "🇬🇧",
    "Deutsch": "🇩🇪",
    "Français": "🇫🇷",
    "Español": "🇪🇸",
    "العربية": "🇸🇦"
}
default_index = list(flags.keys()).index(st.session_state.language)
st.sidebar.image("geneq.jpg", use_container_width=True)

selected_language = st.sidebar.selectbox(
    "Language / Dil / Sprache / Français / Español / العربية",
    options=[f"{flags[lang]} {lang}" for lang in flags],
    index=default_index
)

try:
    selected_language_name = selected_language.split(' ', 1)[1]  
    selected_flag = flags[selected_language_name]
except KeyError:
    selected_language_name = selected_language 
    selected_flag = None  

st.markdown("""
<style>
[data-testid="stSidebarCollapseButton"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)


st.sidebar.markdown("---")
instruction_clicked = st.sidebar.button("📘 Instruction ")

if instruction_clicked or selected_language_name == "Instruction":

    @st.dialog("📘 GeneQuantify User Guide")
    def show_guide():
        st.markdown("""

This guide explains how to properly format your qPCR data, perform ΔΔCt calculations, and interpret the results.

---

### 📌 Data Input Format
 
- Compatible with **Excel copy–paste**. Commas are converted automatically to dots.  

**Example:**

23.1   
22.9   
25.2 

---

### 📊 Example Excel Table
| Group     | Cq | 
|-----------|------|
| Control 1 | 23.1 | 
| Control 2 | 22.9 | 
| Control 3 | 25.2 | 

---

### 🧮 Calculations
1. **ΔCt** = Ct(target) – Ct(reference)  
2. **ΔΔCt** = ΔCt(test) – ΔCt(control)  
3. **Fold Change** = 2^(-ΔΔCt)  

---

### 🔬 Amplification Efficiency — How to Obtain Your E Value

The amplification efficiency (E) tells you how well your PCR reaction doubles the template each cycle.  
**E = 2.0** means perfect doubling (100% efficiency).

---

#### 📌 Method 1 — Standard Curve (Most Common)
Run qPCR on a serial dilution series (e.g. 5 points, 10× dilutions) for each primer pair.  
Your qPCR software (Bio-Rad CFX Manager, Applied Biosystems QuantStudio, Roche LightCycler, etc.) will automatically report the **slope** and **E value** in the standard curve results tab.

| Dilution | log(Concentration) | Ct    |
|----------|--------------------|-------|
| 1:1      | 0                  | 18.2  |
| 1:10     | -1                 | 21.5  |
| 1:100    | -2                 | 24.8  |
| 1:1000   | -3                 | 28.1  |
| 1:10000  | -4                 | 31.4  |

→ The software fits a regression line: **slope ≈ −3.32** → **E = 10^(−1/−3.32) ≈ 2.0 (100%)**  
→ You can also use the **built-in Standard Curve Calculator** in this app (below the efficiency section).

---

#### 📌 Method 2 — Software Tools
- **LinRegPCR** (free): calculates E from raw fluorescence data  
- **qBase+**: multi-reference normalisation with efficiency correction  
- **Bio-Rad CFX Maestro / QuantStudio Design & Analysis**: report E directly

---

#### 📌 Method 3 — Primer/Kit Datasheet
Commercial primer sets often specify validated efficiency values.  
Check the product datasheet or manufacturer's website.

---

#### ✅ Acceptable Range
| E Value | Efficiency | Status     |
|---------|------------|------------|
| 1.8–2.2 | 90–110%    | ✅ Accepted |
| < 1.8   | < 90%      | ⚠️ Low      |
| > 2.2   | > 110%     | ⚠️ High     |

If target and reference efficiencies differ by **> 10%**, the classic ΔΔCt method is unreliable → use **Pfaffl method** instead.

---

#### 🧮 Pfaffl Formula
**Ratio = (E_target ^ ΔCt_target) / (E_ref ^ ΔCt_ref)**  
where ΔCt = Ct_control − Ct_sample for each gene.

---

### 📈 Statistical Tests
- Shapiro–Wilk → checks normality  
- Levene → checks homogeneity of variances  
- Student's t-test / Welch → compare means  
- Mann–Whitney U → non-parametric comparison  

---

### 📄 Outputs
- PDF report  
- CSV file  
- Plots and graphs

---

### 📄 Disclaimer
This application is intended for **research**, **education**, and **preliminary laboratory analysis** only. It is **NOT** designed or validated for clinical diagnosis, treatment decisions, or patient management. The developers do **not** guarantee: - Complete accuracy of calculations or statistical outputs - Compatibility with specific qPCR assays, kits, or platforms - Compliance with clinical laboratory standards - Correctness or validity of user-entered data Users are fully responsible for: - Verifying the accuracy of entered Ct data - Interpreting results appropriately - Confirming findings using validated laboratory methods The developers are **not liable** for any decisions, losses, or damages arising from application use. All clinical decisions must be made by qualified professionals. Contact: **mailtoburhanettin@gmail.com**



""")

    show_guide()
    
language_map = {
    "Türkçe": "tr",
    "Español": "es",
    "English": "en",
    "Français": "fr",
    "Deutsch": "de",
    "العربية": "ar"
}

language_code = language_map.get(selected_language_name, "en")  

translations = {
    "tr": {
        "title": "🧬 GeneQuantify: Gen Ekspresyonu ve Kopya Sayısı Varyasyonu (CNV) Analizi",
        "subtitle": "B. Yalçınkaya tarafından geliştirildi",
        "patient_data_header": "📊 Hasta ve Kontrol Grubu Verisi Girin",
        "num_target_genes": "🔹 Hedef Gen Sayısını Girin",
        "num_patient_groups": "🔹 Hasta Grubu Sayısını Girin",
        "sample_number": "Örnek Numarası",
        "Grup": "Grup",
        "x_axis_title": "Grup Adı",
        "ct_value": "Ct Değeri",
        "reference_ct": "Referans Ct",
        "delta_ct_control": "ΔCt (Kontrol)",
        "delta_ct_patient": "ΔCt (Hasta)",
        "warning_empty_input": "⚠️ Dikkat: Verileri alt alta yazın veya boşluk içeren hücre olmayacak şekilde excelden kopyalayıp yapıştırın.",
        "download_csv": "📥 CSV İndir",
        "generate_pdf": "📥 PDF Raporu Hazırla",
        "pdf_report": "Gen Ekspresyon Analizi Raporu",
        "statistics": "istatistiksel Sonuçlar",
        "nil_mine": "📊 Sonuçlar",
        "gr_tbl": "📋 Giriş Verileri Tablosu",
        "control_group": "🧬 Kontrol Grubu",
        "ctrl_trgt_ct": "🟦 Kontrol Grubu Hedef Gen {i} Ct Değerleri",
        "ctrl_ref_ct": "🟦 Kontrol Grubu Referans Gen {i} Ct Değerleri",
        "hst_trgt_ct": "🩸 Hasta Grubu Hedef Gen {j} Ct Değerleri",
        "hst_ref_ct": "🩸 Hasta Grubu Referans Gen {j} Ct Değerleri",
        "warning_control_ct": "⚠️ Dikkat: Kontrol Grubu {i} verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde Excel'den kopyalayıp yapıştırın.",
        "warning_patient_ct": "⚠️ Dikkat: Hasta grubu Ct verilerini alt alta yazın veya boşluk içeren hücre olmayacak şekilde Excel'den kopyalayıp yapıştırın.",
        "target_gene": "Hedef Gen",
        "reference_gene": "Referans Gen",
        "target_ct": "Hedef Gen Ct",
        "distribution_graph": "Dağılım Grafiği",
        "error_missing_control_data": "⚠️ Hata: Kontrol Grubu için Hedef Gen {i} verileri eksik!",
        "control_group_avg": "Kontrol Grubu Ortalama",
        "avg": "Ortalama",
        "control": "Kontrol",
        "sample": "Örnek",
        "patient": "Hasta",
        "delta_ct_distribution": "ΔCt Dağılımı",
        "delta_ct_value": "ΔCt Değeri",
        "parametric": "Parametrik",
        "non_parametric": "Nonparametrik",
        "t_test": "t-test",
        "mann_whitney_u_test": "Mann-Whitney U testi",
        "welch_t_test": "welch_t_testi",
        "significant": "Anlamlı",
        "insignificant": "Anlamsız",
        "test_type": "Test Türü",
        "test_method": "Kullanılan Test",
        "test_pvalue": "Test P-değeri",
        "significance": "Anlamlılık",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Gen Ekspresyon Değişimi (2^(-ΔΔCt))",
        "regulation_status": "Regülasyon Durumu",
        "no_change": "Değişim Yok",
        "upregulated": "Yukarı Regüle",
        "downregulated": "Aşağı Regüle",
        "report_title": "Gen Ekspresyon Analizi Raporu",
        "input_data_table": "Giriş Verileri Tablosu",
        "results": "Sonuçlar",
        "statistical_results": "📈 İstatistiksel Sonuçlar",
        "statistical_evaluation": "İstatistiksel Değerlendirme",
        "target_gene": "Hedef Gen",
        "patient_group": "🩸 Hasta Grubu",
        "expression_change": "Gen Ekspresyon Değişimi",
        "generate_pdf": "PDF Oluştur",
        "pdf_report": "Gen Ekspresyon Raporu",
        "error_no_data": "Veri bulunamadı, PDF oluşturulamadı.",
        # Efficiency translations
        "efficiency_header": "🔬 Amplifikasyon Etkinliği (Efficiency) Doğrulaması",
        "efficiency_method": "Efficiency Giriş Yöntemi",
        "efficiency_manual": "Manuel E değeri gir",
        "efficiency_slope": "Slope (eğim) ile hesapla",
        "efficiency_target_label": "Hedef Gen {i} Efficiency (E)",
        "efficiency_ref_label": "Referans Gen {i} Efficiency (E)",
        "efficiency_target_slope_label": "Hedef Gen {i} Slope",
        "efficiency_ref_slope_label": "Referans Gen {i} Slope",
        "efficiency_threshold": "Kabul edilebilir efficiency farkı eşiği (%)",
        "efficiency_ok": "✅ Efficiency farkı kabul edilebilir ({diff:.1f}%)",
        "efficiency_warning": "⚠️ Efficiency farkı eşiği aşıyor ({diff:.1f}%) — ΔΔCt yöntemi güvenilir olmayabilir!",
        "efficiency_target_pct": "Hedef Gen Efficiency",
        "efficiency_ref_pct": "Referans Gen Efficiency",
        "efficiency_diff": "Fark",
        "pfaffl_result": "Pfaffl Oranı",
        "pfaffl_header": "Pfaffl Metodu Sonuçları",
        "classic_ddct": "Klasik ΔΔCt Sonucu (2^(-ΔΔCt))",
        "pfaffl_ratio": "Pfaffl Oranı",
        "method_comparison": "📊 Yöntem Karşılaştırması",
        "efficiency_note": "Not: E=2.0 mükemmel etkinliği (100%) temsil eder. Kabul edilen aralık: 1.8–2.2 (90–110%)",
        "statistical_explanation": (
            "İstatistiksel değerlendirme sürecinde veri dağılımı Shapiro-Wilk testi ile analiz edilmiştir. "
            "Normallik sağlanırsa, gruplar arasındaki varyans eşitliği Levene testi ile kontrol edilmiştir. "
            "Varyans eşitliği varsa bağımsız örneklem t-testi, yoksa Welch t-testi uygulanmıştır. "
            "Normal dağılım sağlanmazsa, parametrik olmayan Mann-Whitney U testi kullanılmıştır. "
            "Sonuçların anlamlılığı p < 0.05 kriterine göre belirlenmiştir. "
            "<b>Öneri ve destekleriniz için:</b> Burhanettin Yalçınkaya - mail: mailtoburhanettin@gmail.com"
        )
    },

    "en": {
        "title": "🧬 GeneQuantify: Expression & CNV Analysis",
        "subtitle": "Developed by B. Yalçınkaya",
        "patient_data_header": "📊 Enter Patient and Control Group Data",
        "num_target_genes": "🔹 Enter the Number of Target Genes",
        "num_patient_groups": "🔹 Enter the Number of Patient Groups",
        "sample_number": "Sample Number",
        "Grup": "Group",
        "x_axis_title": "Group Name",
        "ct_value": "Ct Value",
        "reference_ct": "Reference Ct",
        "delta_ct_control": "ΔCt (Control)",
        "delta_ct_patient": "ΔCt (Patient)",
        "warning_empty_input": "⚠️ Warning: Write data one below the other or copy-paste without empty cells from Excel.",
        "download_csv": "📥 Download CSV",
        "generate_pdf": "📥 Prepare PDF Report",
        "pdf_report": "Gene Expression Analysis Report",
        "nil_mine": "📊 Results",
        "gr_tbl": "📋 Input Data Table",
        "control_group": "🧬 Control Group",
        "ctrl_trgt_ct": "🟦 Control Group Target Gene {i} Ct Values",
        "ctrl_ref_ct": "🟦 Control Group Reference Gene {i} Ct Values",
        "hst_trgt_ct": "🩸 Patient Group Target Gene {j} Ct Values",
        "hst_ref_ct": "🩸 Patient Group Reference Gene {j} Ct Values",
        "warning_control_ct": "⚠️ Warning: Control Group {i} data should be entered line by line or copied from Excel without empty cells.",
        "warning_patient_ct": "⚠️ Warning: Enter patient group Ct values line by line or copy-paste from Excel without empty cells.",
        "target_gene": "Target Gene",
        "reference_gene": "Reference Gene",
        "target_ct": "Target Gene Ct", 
        "distribution_graph": "Distribution Graph",
        "error_missing_control_data": "⚠️ Error: Missing data for Target Gene {i} in the Control Group!",
        "control_group_avg": "Control Group Average",
        "avg": "Average",
        "control": "Control",
        "sample": "Sample",
        "patient": "Patient",
        "delta_ct_distribution": "ΔCt Distribution",
        "delta_ct_value": "ΔCt Value",
        "parametric": "Parametric",
        "non_parametric": "Nonparametric",
        "t_test": "t-test",
        "mann_whitney_u_test": "Mann-Whitney U test",
        "welch_t_test": "Welch t-test",
        "significant": "Significant",
        "insignificant": "Insignificant",
        "test_type": "Test Type",
        "test_method": "Test Method",
        "test_pvalue": "Test P-value",
        "significance": "Significance",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Gene Expression Change (2^(-ΔΔCt))",
        "regulation_status": "Regulation Status",
        "no_change": "No Change",
        "upregulated": "Upregulated",
        "downregulated": "Downregulated",
        "report_title": "Gene Expression Analysis Report",
        "input_data_table": "Input Data Table",
        "results": "Results",
        "statistical_results": "📈 Statistical Results",
        "statistical_evaluation": "Statistical Evaluation",
        "target_gene": "Target Gene",
        "patient_group": "🩸 Patient Group",
        "expression_change": "Gene Expression Change",
        "generate_pdf": "Generate PDF",
        "pdf_report": "Gene Expression Report",
        "error_no_data": "No data found, PDF could not be generated.",
        # Efficiency translations
        "efficiency_header": "🔬 Amplification Efficiency Validation",
        "efficiency_method": "Efficiency Input Method",
        "efficiency_manual": "Enter E value manually",
        "efficiency_slope": "Calculate from slope",
        "efficiency_target_label": "Target Gene {i} Efficiency (E)",
        "efficiency_ref_label": "Reference Gene {i} Efficiency (E)",
        "efficiency_target_slope_label": "Target Gene {i} Slope",
        "efficiency_ref_slope_label": "Reference Gene {i} Slope",
        "efficiency_threshold": "Acceptable efficiency difference threshold (%)",
        "efficiency_ok": "✅ Efficiency difference is acceptable ({diff:.1f}%)",
        "efficiency_warning": "⚠️ Efficiency difference exceeds threshold ({diff:.1f}%) — ΔΔCt method may not be reliable!",
        "efficiency_target_pct": "Target Gene Efficiency",
        "efficiency_ref_pct": "Reference Gene Efficiency",
        "efficiency_diff": "Difference",
        "pfaffl_result": "Pfaffl Ratio",
        "pfaffl_header": "Pfaffl Method Results",
        "classic_ddct": "Classic ΔΔCt Result (2^(-ΔΔCt))",
        "pfaffl_ratio": "Pfaffl Ratio",
        "method_comparison": "📊 Method Comparison",
        "efficiency_note": "Note: E=2.0 represents perfect efficiency (100%). Accepted range: 1.8–2.2 (90–110%)",
        "statistical_explanation": (
            "During the statistical evaluation process, data distribution was analyzed using the Shapiro-Wilk test. "
            "If normality was met, variance homogeneity between groups was checked with Levene's test. "
            "If variance was equal, an independent sample t-test was applied; otherwise, a Welch t-test was used. "
            "If normal distribution was not achieved, the non-parametric Mann-Whitney U test was applied. "
            "Significance was determined using the p < 0.05 criterion. "
            "For suggestions and support, Burhanettin Yalçinkaya - email: mailtoburhanettin@gmail.com"
        )
    },

    "de": {
        "title": "🧬 GeneQuantify: Expressions- und CNV-Analyse",
        "subtitle": "Entwickelt von B. Yalçınkaya",
        "patient_data_header": "📊 Geben Sie Patientendaten und Kontrollgruppen ein",
        "num_target_genes": "🔹 Geben Sie die Anzahl der Zielgene ein",
        "num_patient_groups": "🔹 Geben Sie die Anzahl der Patientengruppen ein",
        "sample_number": "Beispielnummer",
        "Grup": "Gruppe",
        "x_axis_title": "Gruppenname",
        "ct_value": "Ct-Wert",
        "reference_ct": "Referenz Ct",
        "delta_ct_control": "ΔCt (Kontrolle)",
        "delta_ct_patient": "ΔCt (Patientendaten)",
        "warning_empty_input": "⚠️ Warnung: Geben Sie die Daten untereinander ein oder kopieren Sie sie ohne leere Zellen aus Excel.",
        "download_csv": "📥 CSV herunterladen",
        "generate_pdf": "📥 PDF-Bericht erstellen",
        "pdf_report": "Genexpression-Analysebericht",
        "nil_mine": "📊 Ergebnisse",
        "gr_tbl": "📋 Eingabedaten Tabelle",
        "control_group": "🧬 Kontrollgruppe",
        "ctrl_trgt_ct": "🟦 Kontrollgruppe Zielgen {i} Ct-Werte",
        "ctrl_ref_ct": "🟦 Kontrollgruppe Referenz {i} Ct-Werte",
        "hst_trgt_ct": "🩸 Patientengruppe Zielgen {j} Ct-Werte",
        "hst_ref_ct": "🩸 Patientengruppe Referenz {j} Ct-Werte",
        "warning_control_ct": "⚠️ Achtung: Kontrollgruppe {i} Daten sollten untereinander eingegeben oder aus Excel ohne leere Zellen eingefügt werden.",
        "warning_patient_ct": "⚠️ Achtung: Geben Sie die Ct-Werte der Patientengruppe untereinander ein oder kopieren Sie sie aus Excel ohne leere Zellen.",
        "target_gene": "Zielgen",
        "reference_gene": "Referenzgen",
        "target_ct": "Zielgen Ct",
        "distribution_graph": "Verteilungsdiagramm",
        "error_missing_control_data": "⚠️ Fehler: Fehlende Daten für Zielgen {i} in der Kontrollgruppe!",
        "control_group_avg": "Durchschnitt der Kontrollgruppe",
        "avg": "Durchschnitt",
        "control": "Kontrolle",
        "sample": "Probe",
        "patient": "Patient",
        "delta_ct_distribution": "ΔCt-Verteilung",
        "delta_ct_value": "ΔCt-Wert",
        "parametric": "Parametrisch",
        "non_parametric": "Nicht parametrisch",
        "t_test": "t-Test",
        "mann_whitney_u_test": "Mann-Whitney U-Test",
        "welch_t_test": "Welch t-Test",
        "significant": "Signifikant",
        "insignificant": "Nicht signifikant",
        "test_type": "Testtyp",
        "test_method": "Verwendeter Test",
        "test_pvalue": "P-Wert",
        "significance": "Signifikanz",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Genexpression Veränderung (2^(-ΔΔCt))",
        "regulation_status": "Regulierungsstatus",
        "no_change": "Keine Veränderung",
        "upregulated": "Hochreguliert",
        "downregulated": "Herunterreguliert",
        "report_title": "Genexpressionsanalysebericht",
        "input_data_table": "Eingabedatentabelle",
        "results": "Ergebnisse",
        "statistical_results": "📈 Statistische Ergebnisse",
        "statistical_evaluation": "Statistische Auswertung",
        "target_gene": "Zielgen",
        "patient_group": "🩸 Patientengruppe",
        "expression_change": "Genexpressionsänderung",
        "generate_pdf": "PDF Erstellen",
        "pdf_report": "Genexpressionsbericht",
        "error_no_data": "Keine Daten gefunden, PDF konnte nicht erstellt werden.",
        # Efficiency translations
        "efficiency_header": "🔬 Amplifikationseffizienz-Validierung",
        "efficiency_method": "Effizienzeingabemethode",
        "efficiency_manual": "E-Wert manuell eingeben",
        "efficiency_slope": "Aus Steigung berechnen",
        "efficiency_target_label": "Zielgen {i} Effizienz (E)",
        "efficiency_ref_label": "Referenzgen {i} Effizienz (E)",
        "efficiency_target_slope_label": "Zielgen {i} Steigung",
        "efficiency_ref_slope_label": "Referenzgen {i} Steigung",
        "efficiency_threshold": "Akzeptable Effizienzdifferenz-Schwelle (%)",
        "efficiency_ok": "✅ Effizienzdifferenz ist akzeptabel ({diff:.1f}%)",
        "efficiency_warning": "⚠️ Effizienzdifferenz überschreitet Schwelle ({diff:.1f}%) — ΔΔCt-Methode möglicherweise nicht zuverlässig!",
        "efficiency_target_pct": "Zielgen-Effizienz",
        "efficiency_ref_pct": "Referenzgen-Effizienz",
        "efficiency_diff": "Differenz",
        "pfaffl_result": "Pfaffl-Verhältnis",
        "pfaffl_header": "Pfaffl-Methode Ergebnisse",
        "classic_ddct": "Klassisches ΔΔCt-Ergebnis (2^(-ΔΔCt))",
        "pfaffl_ratio": "Pfaffl-Verhältnis",
        "method_comparison": "📊 Methodenvergleich",
        "efficiency_note": "Hinweis: E=2.0 steht für perfekte Effizienz (100%). Akzeptierter Bereich: 1.8–2.2 (90–110%)",
        "statistical_explanation": (
            "Während des statistischen Bewertungsprozesses wurde die Datenverteilung mit dem Shapiro-Wilk-Test analysiert. "
            "Wenn die Normalität erfüllt war, wurde die Varianzhomogenität zwischen den Gruppen mit dem Levene-Test überprüft. "
            "War die Varianz gleich, wurde ein unabhängiger Stichprobent-Test angewendet; andernfalls wurde ein Welch-T-Test verwendet. "
            "Wenn keine normale Verteilung vorlag, wurde der nicht-parametrische Mann-Whitney-U-Test angewendet. "
            "Die Signifikanz wurde anhand des Kriteriums p < 0,05 bestimmt. "
            "Für Vorschläge und Unterstützung, Burhanettin Yalçinkaya - E-Mail: mailtoburhanettin@gmail.com"
        )
    },
    
    "fr": {
        "title": "🧬 GeneQuantify : Analyse de l'expression génique et des variations du nombre de copies (CNV)",
        "subtitle": "Développé par B. Yalçınkaya",
        "patient_data_header": "📊 Entrez les données des groupes patients et témoins",
        "num_target_genes": "🔹 Entrez le nombre de gènes cibles",
        "num_patient_groups": "🔹 Entrez le nombre de groupes de patients",
        "sample_number": "Numéro de l'échantillon",
        "Grup": "Groupe",
        "x_axis_title": "Nom du Groupe",
        "ct_value": "Valeur Ct",
        "reference_ct": "Ct de Référence",
        "delta_ct_control": "ΔCt (Contrôle)",
        "delta_ct_patient": "ΔCt (Patient)",
        "warning_empty_input": "⚠️ Avertissement : Entrez les données sous forme de liste ou copiez-collez sans cellules vides depuis Excel.",
        "download_csv": "📥 Télécharger CSV",
        "generate_pdf": "📥 Préparer le Rapport PDF",
        "pdf_report": "Rapport d'Analyse de l'Expression Génétique",
        "nil_mine": "📊 Résultats",
        "gr_tbl": "📋 Tableau des Données d'Entrée",
        "control_group": "🧬 Groupe Contrôle",
        "ctrl_trgt_ct": "🟦 Valeurs Ct du Gène Cible {i} pour le Groupe Contrôle",
        "ctrl_ref_ct": "🟦 Valeurs Ct du Gène Référence {i} pour le Groupe Contrôle",
        "hst_trgt_ct": "🩸 Valeurs Ct du Gène Cible {j} pour le Groupe Patient",
        "hst_ref_ct": "🩸 Valeurs Ct du Gène Référence {j} pour le Groupe Patient",
        "warning_control_ct": "⚠️ Avertissement : Les données du groupe témoin {i} doivent être saisies ligne par ligne ou copiées depuis Excel sans cellules vides.",
        "warning_patient_ct": "⚠️ Avertissement : Entrez les valeurs Ct du groupe patient ligne par ligne ou copiez-les depuis Excel sans cellules vides.",
        "target_gene": "Gène Cible",
        "reference_gene": "Gène Référence",
        "target_ct": "Ct du Gène Cible", 
        "distribution_graph": "Graphique de Distribution",
        "error_missing_control_data": "⚠️ Erreur : Données manquantes pour le Gène Cible {i} dans le Groupe Contrôle!",
        "control_group_avg": "Moyenne du Groupe Contrôle",
        "avg": "Moyenne",
        "control": "Contrôle",
        "sample": "Échantillon",
        "patient": "Patient",
        "delta_ct_distribution": "Distribution ΔCt",
        "delta_ct_value": "Valeur ΔCt",
        "parametric": "Paramétrique",
        "non_parametric": "Non paramétrique",
        "t_test": "Test t",
        "mann_whitney_u_test": "Test Mann-Whitney U",
        "welch_t_test": "Test t de Welch",
        "significant": "Significatif",
        "insignificant": "Non Significatif",
        "test_type": "Type de Test",
        "test_method": "Méthode de Test",
        "test_pvalue": "P-valeur du Test",
        "significance": "Signification",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Changement de l'Expression Génétique (2^(-ΔΔCt))",
        "regulation_status": "Statut de Régulation",
        "no_change": "Aucun Changement",
        "upregulated": "Upregulé",
        "downregulated": "Downregulé",
        "report_title": "Rapport d'Analyse de l'Expression Génétique",
        "input_data_table": "Tableau des Données d'Entrée",
        "results": "Résultats",
        "statistical_results": "📈 Résultats Statistiques",
        "statistical_evaluation": "Évaluation Statistique",
        "target_gene": "Gène Cible",
        "patient_group": "🩸 Groupe Patient",
        "expression_change": "Changement de l'Expression Génétique",
        "generate_pdf": "Générer le PDF",
        "pdf_report": "Rapport sur l'Expression Génétique",
        "error_no_data": "Aucune donnée trouvée, le PDF n'a pas pu être généré.",
        # Efficiency translations
        "efficiency_header": "🔬 Validation de l'Efficacité d'Amplification",
        "efficiency_method": "Méthode de saisie d'efficacité",
        "efficiency_manual": "Entrer la valeur E manuellement",
        "efficiency_slope": "Calculer à partir de la pente",
        "efficiency_target_label": "Efficacité du Gène Cible {i} (E)",
        "efficiency_ref_label": "Efficacité du Gène Référence {i} (E)",
        "efficiency_target_slope_label": "Pente du Gène Cible {i}",
        "efficiency_ref_slope_label": "Pente du Gène Référence {i}",
        "efficiency_threshold": "Seuil de différence d'efficacité acceptable (%)",
        "efficiency_ok": "✅ La différence d'efficacité est acceptable ({diff:.1f}%)",
        "efficiency_warning": "⚠️ La différence d'efficacité dépasse le seuil ({diff:.1f}%) — La méthode ΔΔCt peut ne pas être fiable!",
        "efficiency_target_pct": "Efficacité du Gène Cible",
        "efficiency_ref_pct": "Efficacité du Gène Référence",
        "efficiency_diff": "Différence",
        "pfaffl_result": "Rapport Pfaffl",
        "pfaffl_header": "Résultats de la Méthode Pfaffl",
        "classic_ddct": "Résultat ΔΔCt Classique (2^(-ΔΔCt))",
        "pfaffl_ratio": "Rapport Pfaffl",
        "method_comparison": "📊 Comparaison des Méthodes",
        "efficiency_note": "Note : E=2.0 représente une efficacité parfaite (100%). Plage acceptée : 1.8–2.2 (90–110%)",
        "statistical_explanation": (
            "Au cours du processus d'évaluation statistique, la répartition des données a été analysée à l'aide du test de Shapiro-Wilk. "
            "Si la normalité était remplie, l'homogénéité de la variance entre les groupes a été vérifiée à l'aide du test de Levene. "
            "Si la variance était égale, un test t pour échantillons indépendants a été appliqué, sinon, un test t de Welch a été utilisé. "
            "Si aucune distribution normale n'était atteinte, le test non paramétrique de Mann-Whitney U a été appliqué. "
            "La signification a été déterminée en utilisant le critère p < 0,05. "
            "Pour des suggestions et un soutien, Burhanettin Yalçınkaya - e-mail : mailtoburhanettin@gmail.com"
        )
    },

    "es": {
        "title": "🧬 GeneQuantify: Análisis de Expresión Génica y CNV",
        "subtitle": "Desarrollado por B. Yalçınkaya",
        "patient_data_header": "📊 Ingrese Datos de Grupos de Pacientes y de Control",
        "num_target_genes": "🔹 Ingrese el número de Genes Objetivo",
        "num_patient_groups": "🔹 Ingrese el número de Grupos de Pacientes",
        "sample_number": "Número de muestra",
        "Grup": "Grupo",
        "x_axis_title": "Nombre del Grupo",
        "ct_value": "Valor de Ct",
        "reference_ct": "Ct de Referencia",
        "delta_ct_control": "ΔCt (Control)",
        "delta_ct_patient": "ΔCt (Paciente)",
        "warning_empty_input": "⚠️ Advertencia: Ingrese los datos uno debajo del otro o cópielos sin celdas vacías desde Excel.",
        "download_csv": "📥 Descargar CSV",
        "generate_pdf": "📥 Preparar Informe en PDF",
        "pdf_report": "Informe de Análisis de Expresión Génica",
        "nil_mine": "📊 Resultados",
        "gr_tbl": "📋 Tabla de Datos de Entrada",
        "control_group": "🧬 Grupo Control",
        "ctrl_trgt_ct": "🟦 Valores Ct del Gen Objetivo {i} para el Grupo Control",
        "ctrl_ref_ct": "🟦 Valores Ct del Gen de Referencia {i} para el Grupo Control",
        "hst_trgt_ct": "🩸 Valores Ct del Gen Objetivo {j} para el Grupo Paciente",
        "hst_ref_ct": "🩸 Valores Ct del Gen de Referencia {j} para el Grupo Paciente",
        "warning_control_ct": "⚠️ Advertencia: Los datos del grupo control {i} deben ingresarse fila por fila o copiarse desde Excel sin celdas vacías.",
        "warning_patient_ct": "⚠️ Advertencia: Ingrese los valores de Ct del grupo paciente fila por fila o cópielos desde Excel sin celdas vacías.",
        "target_gene": "Gen Objetivo",
        "reference_gene": "Gen de Referencia",
        "target_ct": "Ct del Gen Objetivo", 
        "distribution_graph": "Gráfico de Distribución",
        "error_missing_control_data": "⚠️ Error: ¡Datos faltantes para el Gen Objetivo {i} en el Grupo Control!",
        "control_group_avg": "Promedio del Grupo Control",
        "avg": "Promedio",
        "control": "Control",
        "sample": "Muestra",
        "patient": "Paciente",
        "delta_ct_distribution": "Distribución ΔCt",
        "delta_ct_value": "Valor ΔCt",
        "parametric": "Paramétrico",
        "non_parametric": "No paramétrico",
        "t_test": "Test t",
        "mann_whitney_u_test": "Test Mann-Whitney U",
        "welch_t_test": "Test t de Welch",
        "significant": "Significativo",
        "insignificant": "No Significativo",
        "test_type": "Tipo de Test",
        "test_method": "Método de Test",
        "test_pvalue": "P-valor del Test",
        "significance": "Significación",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "Cambio de Expresión Génica (2^(-ΔΔCt))",
        "regulation_status": "Estado de Regulación",
        "no_change": "Sin Cambio",
        "upregulated": "Upregulado",
        "downregulated": "Downregulado",
        "report_title": "Informe de Análisis de Expresión Génica",
        "input_data_table": "Tabla de Datos de Entrada",
        "results": "Resultados",
        "statistical_results": "📈 Resultados Estadísticos",
        "statistical_evaluation": "Evaluación Estadística",
        "target_gene": "Gen Objetivo",
        "patient_group": "🩸 Grupo Paciente",
        "expression_change": "Cambio de Expresión Génica",
        "generate_pdf": "Generar PDF",
        "pdf_report": "Informe de Expresión Génica",
        "error_no_data": "No se encontraron datos, no se pudo generar el PDF.",
        # Efficiency translations
        "efficiency_header": "🔬 Validación de Eficiencia de Amplificación",
        "efficiency_method": "Método de entrada de eficiencia",
        "efficiency_manual": "Ingresar valor E manualmente",
        "efficiency_slope": "Calcular desde pendiente",
        "efficiency_target_label": "Eficiencia del Gen Objetivo {i} (E)",
        "efficiency_ref_label": "Eficiencia del Gen de Referencia {i} (E)",
        "efficiency_target_slope_label": "Pendiente del Gen Objetivo {i}",
        "efficiency_ref_slope_label": "Pendiente del Gen de Referencia {i}",
        "efficiency_threshold": "Umbral de diferencia de eficiencia aceptable (%)",
        "efficiency_ok": "✅ La diferencia de eficiencia es aceptable ({diff:.1f}%)",
        "efficiency_warning": "⚠️ La diferencia de eficiencia supera el umbral ({diff:.1f}%) — ¡El método ΔΔCt puede no ser confiable!",
        "efficiency_target_pct": "Eficiencia del Gen Objetivo",
        "efficiency_ref_pct": "Eficiencia del Gen de Referencia",
        "efficiency_diff": "Diferencia",
        "pfaffl_result": "Relación Pfaffl",
        "pfaffl_header": "Resultados del Método Pfaffl",
        "classic_ddct": "Resultado ΔΔCt Clásico (2^(-ΔΔCt))",
        "pfaffl_ratio": "Relación Pfaffl",
        "method_comparison": "📊 Comparación de Métodos",
        "efficiency_note": "Nota: E=2.0 representa eficiencia perfecta (100%). Rango aceptado: 1.8–2.2 (90–110%)",
        "statistical_explanation": (
            "Durante el proceso de evaluación estadística, se analizó la distribución de los datos mediante la prueba de Shapiro-Wilk. "
            "Si se cumplió la normalidad, se verificó la homogeneidad de varianza entre los grupos mediante la prueba de Levene. "
            "Si la varianza era igual, se aplicó la prueba t de muestras independientes; de lo contrario, se utilizó la prueba t de Welch. "
            "Si no se alcanzó una distribución normal, se aplicó la prueba no paramétrica Mann-Whitney U. "
            "La significancia se determinó utilizando el criterio p < 0.05. "
            "Para sugerencias y soporte, Burhanettin Yalçınkaya - correo electrónico: mailtoburhanettin@gmail.com"
        )
    },

    "ar": {
        "title": "🧬 جين كوانتيفاي: تحليل التعبير الجيني وتغير عدد النسخ (CNV)",
        "subtitle": "تم تطويره بواسطة ب. يالجنكايا",
        "patient_data_header": "📊 إدخال بيانات مجموعة المرضى ومجموعة التحكم",
        "num_target_genes": "🔹 إدخال عدد الجينات المستهدفة",
        "num_patient_groups": "🔹 إدخال عدد مجموعات المرضى",
        "sample_number": "رقم العينة",
        "Grup": "مجموعة",
        "x_axis_title": "اسم المجموعة",
        "ct_value": "قيمة Ct",
        "reference_ct": "قيمة Ct المرجعية",
        "delta_ct_control": "ΔCt (التحكم)",
        "delta_ct_patient": "ΔCt (المريض)",
        "warning_empty_input": "⚠️ تحذير: أدخل البيانات واحدًا تلو الآخر أو انسخها دون خلايا فارغة من Excel.",
        "download_csv": "📥 تحميل CSV",
        "generate_pdf": "📥 إعداد تقرير PDF",
        "pdf_report": "تقرير تحليل التعبير الجيني",
        "nil_mine": "📊 النتائج",
        "gr_tbl": "📋 جدول بيانات الإدخال",
        "control_group": "🧬 مجموعة التحكم",
        "ctrl_trgt_ct": "🟦 قيم Ct الجين المستهدف {i} لمجموعة التحكم",
        "ctrl_ref_ct": "🟦 قيم Ct الجين المرجعي {i} لمجموعة التحكم",
        "hst_trgt_ct": "🩸 قيم Ct الجين المستهدف {j} لمجموعة المرضى",
        "hst_ref_ct": "🩸 قيم Ct الجين المرجعي {j} لمجموعة المرضى",
        "warning_control_ct": "⚠️ تحذير: يجب إدخال بيانات مجموعة التحكم {i} سطرًا بسطر أو نسخها من Excel دون خلايا فارغة.",
        "warning_patient_ct": "⚠️ تحذير: أدخل قيم Ct لمجموعة المرضى سطرًا بسطر أو انسخها من Excel دون خلايا فارغة.",
        "target_gene": "الجين المستهدف",
        "reference_gene": "الجين المرجعي",
        "target_ct": "قيمة Ct الجين المستهدف", 
        "distribution_graph": "رسم بياني للتوزيع",
        "error_missing_control_data": "⚠️ خطأ: بيانات مفقودة للجين المستهدف {i} في مجموعة التحكم!",
        "control_group_avg": "متوسط مجموعة التحكم",
        "avg": "متوسط",
        "control": "التحكم",
        "sample": "عينة",
        "patient": "مريض",
        "delta_ct_distribution": "توزيع ΔCt",
        "delta_ct_value": "قيمة ΔCt",
        "parametric": "معلمي",
        "non_parametric": "غير معلمي",
        "t_test": "اختبار t",
        "mann_whitney_u_test": "اختبار مان-ويتني U",
        "welch_t_test": "اختبار ويلش t",
        "significant": "مهم",
        "insignificant": "غير مهم",
        "test_type": "نوع الاختبار",
        "test_method": "طريقة الاختبار",
        "test_pvalue": "قيمة P للاختبار",
        "significance": "الدلالة",
        "delta_delta_ct": "ΔΔCt",
        "gene_expression_change": "تغيير التعبير الجيني (2^(-ΔΔCt))",
        "regulation_status": "حالة التنظيم",
        "no_change": "لا تغيير",
        "upregulated": "مرتفع التنظيم",
        "downregulated": "منخفض التنظيم",
        "report_title": "تقرير تحليل التعبير الجيني",
        "input_data_table": "جدول بيانات الإدخال",
        "results": "النتائج",
        "statistical_results": "📈 النتائج الإحصائية",
        "statistical_evaluation": "التقييم الإحصائي",
        "target_gene": "الجين المستهدف",
        "patient_group": "🩸 مجموعة المرضى",
        "expression_change": "تغيير التعبير الجيني",
        "generate_pdf": "توليد تقرير PDF",
        "pdf_report": "تقرير التعبير الجيني",
        "error_no_data": "لم يتم العثور على بيانات، لم يتم إنشاء التقرير PDF.",
        # Efficiency translations
        "efficiency_header": "🔬 التحقق من كفاءة التضخيم",
        "efficiency_method": "طريقة إدخال الكفاءة",
        "efficiency_manual": "إدخال قيمة E يدويًا",
        "efficiency_slope": "الحساب من الانحدار",
        "efficiency_target_label": "كفاءة الجين المستهدف {i} (E)",
        "efficiency_ref_label": "كفاءة الجين المرجعي {i} (E)",
        "efficiency_target_slope_label": "انحدار الجين المستهدف {i}",
        "efficiency_ref_slope_label": "انحدار الجين المرجعي {i}",
        "efficiency_threshold": "عتبة فرق الكفاءة المقبول (%)",
        "efficiency_ok": "✅ فرق الكفاءة مقبول ({diff:.1f}%)",
        "efficiency_warning": "⚠️ فرق الكفاءة يتجاوز العتبة ({diff:.1f}%) — قد لا تكون طريقة ΔΔCt موثوقة!",
        "efficiency_target_pct": "كفاءة الجين المستهدف",
        "efficiency_ref_pct": "كفاءة الجين المرجعي",
        "efficiency_diff": "الفرق",
        "pfaffl_result": "نسبة Pfaffl",
        "pfaffl_header": "نتائج طريقة Pfaffl",
        "classic_ddct": "نتيجة ΔΔCt الكلاسيكية (2^(-ΔΔCt))",
        "pfaffl_ratio": "نسبة Pfaffl",
        "method_comparison": "📊 مقارنة الطرق",
        "efficiency_note": "ملاحظة: E=2.0 تمثل الكفاءة المثالية (100%). النطاق المقبول: 1.8–2.2 (90–110%)",
        "statistical_explanation": (
            "أثناء عملية التقييم الإحصائي، تم تحليل توزيع البيانات باستخدام اختبار شابيرو-ويلك. "
            "إذا تم تحقيق التوزيع الطبيعي، تم التحقق من تجانس التباين بين المجموعات باستخدام اختبار ليفين. "
            "إذا كانت التباين متساويًا، تم تطبيق اختبار t للعينة المستقلة، وإذا لم يكن كذلك، تم استخدام اختبار t ويلش. "
            "إذا لم يتم تحقيق التوزيع الطبيعي، تم تطبيق اختبار مان-ويتني U غير المعلمي. "
            "تم تحديد الدلالة باستخدام المعيار p < 0.05. "
            "للاقتراحات والدعم، بورهانيتين يالجنكايا - البريد الإلكتروني: mailtoburhanettin@gmail.com"
        )
    }
}

                  
st.markdown(f"<h3>{translations[language_code]['title']}</h3>", unsafe_allow_html=True)
st.markdown(f"<h4>{translations[language_code]['patient_data_header']}</h4>", unsafe_allow_html=True)

num_target_genes = st.number_input(translations[language_code]["num_target_genes"], min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(translations[language_code]["num_patient_groups"], min_value=1, step=1, key="patient_count")

# ─── EFFICIENCY VALIDATION SECTION ───────────────────────────────────────────
st.markdown("---")

# Header + ℹ️ tooltip side by side
eff_col_title, eff_col_help = st.columns([8, 1])
with eff_col_title:
    st.markdown(f"<h4>{translations[language_code]['efficiency_header']}</h4>", unsafe_allow_html=True)
with eff_col_help:
    with st.popover("ℹ️"):
        st.markdown("""
**How to obtain your Efficiency (E) value:**

**Method 1 — Standard Curve** *(recommended)*  
Run qPCR on 4–5 serial dilutions (e.g. 10× each) for each primer.  
Your qPCR software will report a **slope** → enter it below, or use the **Standard Curve Calculator** in the expander below.  
`E = 10^(−1 / slope)`

**Method 2 — Software tools**  
- LinRegPCR (free download)  
- qBase+, Bio-Rad CFX Maestro, QuantStudio

**Method 3 — Primer/Kit datasheet**  
Manufacturer often validates and publishes E for commercial primer sets.

**Acceptable range:** E = 1.8–2.2 (90–110%)  
**If |E_target − E_ref| > 10% → use Pfaffl method**
""")

st.info(translations[language_code]["efficiency_note"])

# ─── STANDARD CURVE CALCULATOR ───────────────────────────────────────────────
with st.expander("📐 Standard Curve Calculator — Calculate E from dilution series", expanded=False):
    st.markdown("""
Enter your serial dilution Ct values below. The calculator will fit a linear regression,
compute the slope, R², and amplification efficiency automatically.

**How to use:**  
1. Run qPCR on serial dilutions (e.g. undiluted, 1:10, 1:100, 1:1000, 1:10000)  
2. Enter the mean Ct for each dilution below  
3. Read off slope, E, and R²  
""")

    sc_col1, sc_col2 = st.columns(2)
    with sc_col1:
        sc_gene_label = st.text_input("Gene / Primer label", value="Target Gene 1", key="sc_label")
        sc_num_points = st.number_input("Number of dilution points", min_value=3, max_value=10, value=5, step=1, key="sc_npts")

    with sc_col2:
        st.markdown("**Dilution factor** (e.g. 10 for 10-fold dilutions)")
        sc_dilution_factor = st.number_input("Dilution factor", min_value=2, max_value=100, value=10, step=1, key="sc_dilfactor")
        st.markdown("**Starting concentration** (arbitrary units, e.g. 1)")
        sc_start_conc = st.number_input("Starting concentration", min_value=0.0001, value=1.0, format="%.4f", key="sc_startconc")

    st.markdown("**Enter mean Ct for each dilution:**")
    sc_ct_cols = st.columns(min(sc_num_points, 5))
    sc_ct_values = []
    sc_log_concs = []
    for pt in range(sc_num_points):
        conc = sc_start_conc / (sc_dilution_factor ** pt)
        log_c = np.log10(conc)
        col_idx = pt % 5
        with sc_ct_cols[col_idx]:
            ct_val = st.number_input(
                f"Dil. {pt+1}\n(log={log_c:.2f})",
                value=18.0 + pt * 3.32,
                step=0.01, format="%.2f",
                key=f"sc_ct_{pt}"
            )
            sc_ct_values.append(ct_val)
            sc_log_concs.append(log_c)

    if st.button("📊 Calculate Efficiency", key="sc_calc"):
        sc_log_concs_arr = np.array(sc_log_concs)
        sc_ct_arr = np.array(sc_ct_values)

        # Linear regression: Ct = slope * log(conc) + intercept
        slope_val, intercept_val, r_val, p_val, se_val = stats.linregress(sc_log_concs_arr, sc_ct_arr)
        r2 = r_val ** 2
        E_calc = 10 ** (-1.0 / slope_val) if slope_val != 0 else float('nan')
        E_pct = (E_calc - 1) * 100

        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        res_col1.metric("Slope", f"{slope_val:.4f}")
        res_col2.metric("E value", f"{E_calc:.4f}")
        res_col3.metric("Efficiency %", f"{E_pct:.1f}%")
        res_col4.metric("R²", f"{r2:.4f}")

        if 1.8 <= E_calc <= 2.2 and r2 >= 0.99:
            st.success(f"✅ Excellent! E={E_calc:.4f} ({E_pct:.1f}%), R²={r2:.4f} — Use this E value in the efficiency section below.")
        elif 1.8 <= E_calc <= 2.2:
            st.warning(f"⚠️ E is acceptable ({E_pct:.1f}%) but R²={r2:.4f} is below 0.99 — check your dilution series.")
        else:
            st.error(f"❌ E={E_calc:.4f} ({E_pct:.1f}%) is outside acceptable range (90–110%). Review your primer design or dilution series.")

        # Plot standard curve
        x_fit = np.linspace(min(sc_log_concs_arr), max(sc_log_concs_arr), 100)
        y_fit = slope_val * x_fit + intercept_val

        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=sc_log_concs_arr, y=sc_ct_arr,
            mode='markers', name='Data points',
            marker=dict(size=10, color='#4C72B0')
        ))
        fig_sc.add_trace(go.Scatter(
            x=x_fit, y=y_fit,
            mode='lines', name=f'Fit (slope={slope_val:.4f})',
            line=dict(color='red', dash='dash')
        ))
        fig_sc.update_layout(
            title=f"Standard Curve — {sc_gene_label} | E={E_calc:.4f} ({E_pct:.1f}%), R²={r2:.4f}",
            xaxis_title="log₁₀(Concentration)",
            yaxis_title="Ct",
            height=350
        )
        st.plotly_chart(fig_sc, use_container_width=True)
        st.info(f"💡 Copy slope **{slope_val:.4f}** or E value **{E_calc:.4f}** into the efficiency inputs below.")

# ─────────────────────────────────────────────────────────────────────────────

efficiency_method = st.radio(
    translations[language_code]["efficiency_method"],
    options=[
        translations[language_code]["efficiency_manual"],
        translations[language_code]["efficiency_slope"]
    ],
    key="eff_method",
    horizontal=True
)

efficiency_threshold = st.number_input(
    translations[language_code]["efficiency_threshold"],
    min_value=1.0,
    max_value=50.0,
    value=10.0,
    step=0.5,
    key="eff_threshold",
    help="Recommended: 10% (MIQE guidelines). If |E_target − E_ref| > this value, ΔΔCt may be unreliable."
)

# Store efficiency values per gene
gene_efficiencies = {}  # {gene_index: {"target_E": float, "ref_E": float}}

use_slope = (efficiency_method == translations[language_code]["efficiency_slope"])

for i in range(num_target_genes):
    with st.expander(f"🔬 {translations[language_code]['target_gene']} {i+1} — Efficiency", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            if use_slope:
                target_slope = st.number_input(
                    translations[language_code]["efficiency_target_slope_label"].format(i=i+1),
                    value=-3.32, step=0.01, format="%.4f",
                    key=f"target_slope_{i}",
                    help="Enter slope from your qPCR software standard curve output. Typical range: −3.1 to −3.6"
                )
                target_E = 10 ** (-1.0 / target_slope) if target_slope != 0 else 2.0
                st.markdown(f"**E (target) = {target_E:.4f}** ({(target_E - 1) * 100:.1f}%)")
            else:
                target_E = st.number_input(
                    translations[language_code]["efficiency_target_label"].format(i=i+1),
                    min_value=1.0, max_value=3.0, value=2.0, step=0.01, format="%.4f",
                    key=f"target_E_{i}",
                    help="E=2.0 = 100% (perfect). Acceptable range: 1.8–2.2. Obtain from standard curve or primer datasheet."
                )
                st.markdown(f"**{(target_E - 1) * 100:.1f}%**")

        with col2:
            if use_slope:
                ref_slope = st.number_input(
                    translations[language_code]["efficiency_ref_slope_label"].format(i=i+1),
                    value=-3.32, step=0.01, format="%.4f",
                    key=f"ref_slope_{i}",
                    help="Enter slope from your qPCR software standard curve output for the reference gene."
                )
                ref_E = 10 ** (-1.0 / ref_slope) if ref_slope != 0 else 2.0
                st.markdown(f"**E (ref) = {ref_E:.4f}** ({(ref_E - 1) * 100:.1f}%)")
            else:
                ref_E = st.number_input(
                    translations[language_code]["efficiency_ref_label"].format(i=i+1),
                    min_value=1.0, max_value=3.0, value=2.0, step=0.01, format="%.4f",
                    key=f"ref_E_{i}",
                    help="E=2.0 = 100% (perfect). Obtain from standard curve or primer datasheet for the reference gene."
                )
                st.markdown(f"**{(ref_E - 1) * 100:.1f}%**")

        # Efficiency difference check
        target_pct = (target_E - 1) * 100
        ref_pct = (ref_E - 1) * 100
        diff = abs(target_pct - ref_pct)

        if diff <= efficiency_threshold:
            st.success(translations[language_code]["efficiency_ok"].format(diff=diff))
        else:
            st.warning(translations[language_code]["efficiency_warning"].format(diff=diff))

        # Efficiency gauge chart
        fig_eff = go.Figure()
        fig_eff.add_trace(go.Bar(
            x=[translations[language_code]["efficiency_target_pct"],
               translations[language_code]["efficiency_ref_pct"]],
            y=[target_pct, ref_pct],
            marker_color=["#4C72B0", "#DD8452"],
            text=[f"{target_pct:.1f}%", f"{ref_pct:.1f}%"],
            textposition="outside"
        ))
        fig_eff.add_hline(y=90, line_dash="dash", line_color="green",
                          annotation_text="90% (min)", annotation_position="right")
        fig_eff.add_hline(y=110, line_dash="dash", line_color="green",
                          annotation_text="110% (max)", annotation_position="right")
        fig_eff.update_layout(
            title=f"{translations[language_code]['target_gene']} {i+1} — Amplification Efficiency (%)",
            yaxis=dict(title="Efficiency (%)", range=[0, 130]),
            height=300
        )
        st.plotly_chart(fig_eff, use_container_width=True)

        gene_efficiencies[i] = {"target_E": target_E, "ref_E": ref_E}

st.markdown("---")
# ─────────────────────────────────────────────────────────────────────────────

def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

# ─── geNorm M-value stability ─────────────────────────────────────────────────
def compute_genorm_m(ref_ct_matrix):
    """
    ref_ct_matrix: 2D numpy array, shape (n_refs, n_samples)
    Returns M-values for each reference gene (lower = more stable).
    Vandesompele et al. 2002 algorithm.
    """
    n_refs, n_samples = ref_ct_matrix.shape
    if n_refs < 2:
        return np.array([0.0])
    m_values = []
    for i in range(n_refs):
        pairwise_vars = []
        for j in range(n_refs):
            if i == j:
                continue
            ratio = ref_ct_matrix[i] - ref_ct_matrix[j]   # log2 ratio in Ct space
            pairwise_vars.append(np.std(ratio, ddof=1) if len(ratio) > 1 else 0.0)
        m_values.append(np.mean(pairwise_vars))
    return np.array(m_values)

def compute_cv(ct_values):
    """Coefficient of variation (%) for a 1D array of Ct values."""
    if len(ct_values) < 2 or np.mean(ct_values) == 0:
        return 0.0
    return (np.std(ct_values, ddof=1) / np.mean(ct_values)) * 100

def geometric_mean_ct(ct_arrays):
    """
    Compute per-sample geometric mean of multiple reference genes.
    ct_arrays: list of 1D arrays (each = one ref gene, all same length n_samples)
    Returns 1D array of length n_samples.
    """
    stacked = np.vstack(ct_arrays)   # shape (n_refs, n_samples)
    return np.mean(stacked, axis=0)  # arithmetic mean in Ct = geometric mean of expression

# ─── OUTLIER DETECTION FUNCTIONS ─────────────────────────────────────────────
def detect_outliers_grubbs(data, alpha=0.05):
    """
    Grubbs test for a single outlier (two-sided).
    Returns list of outlier indices. Requires n >= 3.
    Grubbs 1969; commonly used in qPCR Ct data QC.
    """
    data = np.array(data, dtype=float)
    n = len(data)
    if n < 3:
        return []
    outlier_indices = []
    working = data.copy()
    original_indices = list(range(n))
    while len(working) >= 3:
        mean_w = np.mean(working)
        std_w  = np.std(working, ddof=1)
        if std_w == 0:
            break
        g_vals = np.abs(working - mean_w) / std_w
        max_idx = np.argmax(g_vals)
        G = g_vals[max_idx]
        # Critical value (two-sided, approximate)
        t_crit = stats.t.ppf(1 - alpha / (2 * len(working)), df=len(working) - 2)
        G_crit = ((len(working) - 1) / np.sqrt(len(working))) * \
                 np.sqrt(t_crit**2 / (len(working) - 2 + t_crit**2))
        if G > G_crit:
            outlier_indices.append(original_indices[max_idx])
            original_indices.pop(max_idx)
            working = np.delete(working, max_idx)
        else:
            break
    return outlier_indices

def detect_outliers_iqr(data, multiplier=1.5):
    """
    IQR-based outlier detection (Tukey fences).
    Returns list of outlier indices.
    """
    data = np.array(data, dtype=float)
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return [i for i, v in enumerate(data) if v < lower or v > upper]

def render_outlier_ui(data, label, key_prefix, method):
    """
    Show detected outliers, let user confirm exclusion via checkboxes.
    Returns cleaned array (with confirmed outliers removed) and list of excluded indices.
    """
    data = np.array(data, dtype=float)
    if method == "Grubbs":
        detected = detect_outliers_grubbs(data)
    else:
        detected = detect_outliers_iqr(data)

    if not detected:
        return data, []

    st.warning(
        f"⚠️ **Potential outlier(s) detected in {label}** "
        f"({method} test): Sample(s) **{[i+1 for i in detected]}** "
        f"— values: **{[round(data[i], 3) for i in detected]}**\n\n"
        f"Select which samples to exclude from analysis:"
    )

    excluded = []
    for idx in detected:
        confirm = st.checkbox(
            f"Exclude Sample {idx+1}  (Ct = {data[idx]:.3f}) from {label}",
            value=False,
            key=f"{key_prefix}_excl_{idx}"
        )
        if confirm:
            excluded.append(idx)

    if excluded:
        cleaned = np.delete(data, excluded)
        st.info(
            f"ℹ️ {len(excluded)} sample(s) excluded from {label}. "
            f"Remaining n = {len(cleaned)}. "
            f"Excluded values will be flagged in the results table and PDF report."
        )
        return cleaned, excluded
    return data, []
# ─────────────────────────────────────────────────────────────────────────────

# ─── MULTI-REFERENCE GENE SETTINGS ───────────────────────────────────────────
st.markdown("---")
st.markdown("### 📚 Reference Gene Settings")

ref_info_col, ref_warn_col = st.columns([3, 2])
with ref_info_col:
    num_ref_genes = st.number_input(
        "Number of reference genes per target gene",
        min_value=1, max_value=10, value=1, step=1,
        key="num_ref_genes",
        help="MIQE guidelines recommend ≥2 validated reference genes for robust normalization."
    )
with ref_warn_col:
    if num_ref_genes == 1:
        st.warning(
            "⚠️ **Methodological note:** Using a single reference gene is a meaningful "
            "constraint on normalization robustness. MIQE guidelines (Bustin et al. 2009) "
            "recommend using **≥ 2 validated reference genes** and assessing their stability "
            "with tools such as geNorm or NormFinder. Consider adding a second reference gene "
            "to strengthen your conclusions."
        )
    else:
        st.success(
            f"✅ {num_ref_genes} reference genes selected. "
            "Geometric mean normalization and geNorm M-value stability will be calculated automatically."
        )

if num_ref_genes > 1:
    with st.expander("ℹ️ About multi-reference normalization", expanded=False):
        st.markdown("""
**Geometric mean normalization** (Vandesompele et al. 2002)  
The normalization factor (NF) is the arithmetic mean of Ct values across all reference genes per sample,
which corresponds to the geometric mean of their expression levels.  
`NF_sample = mean(Ct_ref1, Ct_ref2, ..., Ct_refN)` for each sample  
`ΔCt = Ct_target − NF`

**geNorm M-value** (stability score)  
For each reference gene, M = average standard deviation of log-ratios against all other reference genes.  
**Lower M = more stable.** MIQE-recommended threshold: M < 0.5 (strict) or M < 1.0 (acceptable).

**CV (Coefficient of Variation)**  
`CV = (SD / mean) × 100%` of raw Ct values across all samples.  
Lower CV indicates less variation and better stability as a reference.

**Reference:** Vandesompele J et al. *Genome Biology* 2002; Bustin SA et al. *Clin Chem* 2009 (MIQE).
""")

st.markdown("---")
# ─────────────────────────────────────────────────────────────────────────────

# ─── OUTLIER DETECTION SETTINGS ──────────────────────────────────────────────
st.markdown("### 🔍 Outlier Detection Settings")

out_col1, out_col2, out_col3 = st.columns([2, 2, 3])
with out_col1:
    outlier_enabled = st.checkbox(
        "Enable outlier detection",
        value=True,
        key="outlier_enabled",
        help="Detects statistically extreme Ct values that may reflect technical errors."
    )
with out_col2:
    outlier_method = st.radio(
        "Detection method",
        options=["Grubbs", "IQR"],
        key="outlier_method",
        horizontal=True,
        help="Grubbs: best for normally distributed data, detects one outlier at a time. "
             "IQR: non-parametric, robust for skewed distributions."
    )
with out_col3:
    if outlier_method == "Grubbs":
        grubbs_alpha = st.number_input(
            "Significance level (α)",
            min_value=0.01, max_value=0.10, value=0.05, step=0.01, format="%.2f",
            key="grubbs_alpha",
            help="α = 0.05 is standard. Lower α = more conservative (fewer outliers flagged)."
        )
        iqr_multiplier = 1.5
    else:
        iqr_multiplier = st.number_input(
            "IQR multiplier (k)",
            min_value=1.0, max_value=3.0, value=1.5, step=0.25, format="%.2f",
            key="iqr_mult",
            help="k=1.5 = standard Tukey fences. k=3.0 = extreme outliers only."
        )
        grubbs_alpha = 0.05

with st.expander("ℹ️ About outlier detection in qPCR", expanded=False):
    st.markdown("""
**Why outlier detection matters in qPCR**

Technical variability is inherent to qPCR: pipetting errors, bubble formation, 
inhibitor carry-over, or RNA quality variation can produce Ct values that are 
statistically inconsistent with the rest of a replicate group. 
Including such values inflates variance, biases means, and can lead to false 
conclusions — particularly in clinical datasets with small sample sizes.

**When this limitation becomes critical:**
- Small groups (n < 5): a single erroneous Ct shifts the mean substantially
- High biological variability (e.g. tumour heterogeneity, clinical cohorts)
- Technical triplicates where one replicate diverges > 0.5 Ct from the others
- Low-abundance targets with Ct > 35, where noise dominates

**Grubbs test** *(Grubbs 1969)*  
Assumes normality. Tests whether the most extreme value is a statistically 
significant outlier (p < α). Iterates until no further outliers are found.  
Best for: replicate Ct values from a single experimental group.

**IQR method** *(Tukey 1977)*  
Non-parametric. Flags values outside Q1 − k×IQR or Q3 + k×IQR.  
Best for: larger groups or non-normal distributions.

**Important:** Outlier exclusion requires **biological or technical justification**. 
This tool flags candidates — the final decision always rests with the researcher.  
All exclusions are logged and reported in the PDF output.

**References:** Grubbs FE. *Technometrics* 1969; Tukey JW. *Exploratory Data Analysis* 1977;  
Bustin SA et al. *Clin Chem* 2009 (MIQE guidelines).
""")

st.markdown("---")
# ─────────────────────────────────────────────────────────────────────────────
input_values_table = []
data = []
stats_data = []

last_control_delta_ct = None
last_gene_index = None

control_group = translations[language_code]["control_group"]
target_gene = translations[language_code]["target_gene"]
reference_gene = translations[language_code]["reference_gene"]
ct_value = translations[language_code]["ct_value"]
patient_group = translations[language_code]["patient_group"]

# Kontrol Grubu Verileri
for i in range(num_target_genes):
    st.markdown(
        f"<h4>{translations[language_code]['control_group']} {i+1} - {translations[language_code]['target_gene']} {i+1}</h4>",
        unsafe_allow_html=True
    )

    control_target_ct = st.text_area(
        f"{translations[language_code]['control_group']} {i+1} - {translations[language_code]['target_gene']} {i+1} - {translations[language_code]['ct_value']}",
        key=f"control_target_ct_{i}"
    )

    # ── Multi-reference gene input (Control) ─────────────────────────────────
    ctrl_ref_arrays = []
    ctrl_ref_names  = []
    all_ctrl_refs_valid = True

    for r in range(num_ref_genes):
        ref_label = f"Ref Gene {r+1}" if num_ref_genes > 1 else translations[language_code]["reference_gene"]
        ctrl_ref_ct_raw = st.text_area(
            f"{translations[language_code]['control_group']} {i+1} — {ref_label} {i+1} — {translations[language_code]['ct_value']}",
            key=f"control_reference_ct_{i}_{r}"
        )
        parsed = parse_input_data(ctrl_ref_ct_raw)
        if len(parsed) == 0:
            all_ctrl_refs_valid = False
        else:
            ctrl_ref_arrays.append(parsed)
            ctrl_ref_names.append(f"Ref Gene {r+1}")

    control_target_ct_values = np.array(parse_input_data(control_target_ct))

    if len(control_target_ct_values) == 0 or not all_ctrl_refs_valid or len(ctrl_ref_arrays) == 0:
        st.error(translations[language_code]["warning_control_ct"].format(i=i+1))
        continue

    # Trim all arrays to common length
    min_control_len = min(len(control_target_ct_values), *[len(a) for a in ctrl_ref_arrays])
    control_target_ct_values = control_target_ct_values[:min_control_len]
    ctrl_ref_arrays = [a[:min_control_len] for a in ctrl_ref_arrays]

    # ── Outlier detection — Control Target Ct ────────────────────────────────
    ctrl_excluded_target = []  # always initialized
    if outlier_enabled and len(control_target_ct_values) >= 3:
        detected_ctrl_tgt = detect_outliers_grubbs(control_target_ct_values, alpha=grubbs_alpha) \
                            if outlier_method == "Grubbs" \
                            else detect_outliers_iqr(control_target_ct_values, multiplier=iqr_multiplier)
        if detected_ctrl_tgt:
            control_target_ct_values, ctrl_excluded_target = render_outlier_ui(
                control_target_ct_values,
                f"Control Group {i+1} — Target Gene {i+1}",
                f"ctrl_tgt_{i}",
                outlier_method
            )
            if ctrl_excluded_target:
                keep_indices = [k for k in range(min_control_len) if k not in ctrl_excluded_target]
                ctrl_ref_arrays = [a[keep_indices] for a in ctrl_ref_arrays]
                min_control_len = len(keep_indices)

    # ── geNorm + CV stability (shown when ≥2 ref genes) ──────────────────────
    if num_ref_genes >= 2:
        ref_matrix = np.vstack(ctrl_ref_arrays)   # (n_refs, n_samples)
        m_values   = compute_genorm_m(ref_matrix)
        cv_values  = [compute_cv(a) for a in ctrl_ref_arrays]

        unstable_ctrl = [r for r, m in enumerate(m_values) if m >= 1.0]
        borderline_ctrl = [r for r, m in enumerate(m_values) if 0.5 <= m < 1.0]

        st.markdown(f"##### 📊 Reference Gene Stability — Control Group {i+1}")
        stab_cols = st.columns(num_ref_genes)
        for r, col in enumerate(stab_cols):
            m_ok = m_values[r] < 1.0
            cv_ok = cv_values[r] < 5.0
            with col:
                st.metric(
                    label=f"Ref Gene {r+1}",
                    value=f"M = {m_values[r]:.3f}",
                    delta=f"CV = {cv_values[r]:.2f}%"
                )
                if m_ok and cv_ok:
                    st.caption("✅ Stable")
                elif m_ok or cv_ok:
                    st.caption("⚠️ Borderline")
                else:
                    st.caption("❌ Unstable — M ≥ 1.0")

        # Stability bar chart
        fig_stab = go.Figure()
        fig_stab.add_trace(go.Bar(
            name="geNorm M-value",
            x=[f"Ref {r+1}" for r in range(num_ref_genes)],
            y=m_values,
            marker_color=["#2ecc71" if m < 0.5 else "#f39c12" if m < 1.0 else "#e74c3c" for m in m_values],
            text=[f"{m:.3f}" for m in m_values],
            textposition="outside"
        ))
        fig_stab.add_hline(y=0.5, line_dash="dot", line_color="green",
                           annotation_text="M=0.5 (strict)", annotation_position="right")
        fig_stab.add_hline(y=1.0, line_dash="dash", line_color="orange",
                           annotation_text="M=1.0 (acceptable)", annotation_position="right")
        fig_stab.update_layout(
            title=f"geNorm M-value — Control Group {i+1} Reference Genes",
            yaxis_title="M-value (lower = more stable)",
            height=280
        )
        st.plotly_chart(fig_stab, use_container_width=True)

        # ── Stability warnings ────────────────────────────────────────────────
        if unstable_ctrl:
            unstable_names = ", ".join([f"Ref Gene {r+1}" for r in unstable_ctrl])
            st.warning(
                f"⚠️ **Unstable reference gene(s) detected in Control Group {i+1}: {unstable_names}**\n\n"
                f"geNorm M-value ≥ 1.0 indicates that the expression of this gene varies "
                f"considerably across samples, which may distort normalization.\n\n"
                f"**Analysis will continue**, but results should be interpreted with caution.\n\n"
                f"**Recommendations:**\n"
                f"- Verify Ct values for {unstable_names} — check for pipetting errors or outliers\n"
                f"- Consider replacing {unstable_names} with a more stable reference gene\n"
                f"- If only 2 reference genes are used and one is unstable, results rely entirely "
                f"on the remaining gene — consider adding a third validated reference\n"
                f"- Consult: Vandesompele et al. *Genome Biology* 2002 for geNorm methodology"
            )
        elif borderline_ctrl:
            borderline_names = ", ".join([f"Ref Gene {r+1}" for r in borderline_ctrl])
            st.info(
                f"ℹ️ **Borderline stability in Control Group {i+1}: {borderline_names}** (M = 0.5–1.0)\n\n"
                f"Expression stability is acceptable per MIQE guidelines, but not ideal. "
                f"Consider validating with an additional reference gene for greater confidence."
            )
        else:
            st.success(
                f"✅ All reference genes in Control Group {i+1} are stable (M < 0.5). "
                f"Normalization quality is excellent."
            )

    # ── Compute normalization factor (geometric mean of refs) ─────────────────
    # Re-sync min_control_len to actual array lengths after any outlier removal
    min_control_len = min(len(control_target_ct_values), *[len(a) for a in ctrl_ref_arrays])
    control_target_ct_values = control_target_ct_values[:min_control_len]
    ctrl_ref_arrays = [a[:min_control_len] for a in ctrl_ref_arrays]

    ctrl_norm_factor = geometric_mean_ct(ctrl_ref_arrays)   # per-sample NF
    control_delta_ct = control_target_ct_values - ctrl_norm_factor

    # For table: show first ref gene Ct as representative; NF shown separately
    control_reference_ct_values = ctrl_ref_arrays[0]   # kept for legacy table column

    average_control_delta_ct = np.mean(control_delta_ct) if len(control_delta_ct) > 0 else None
    sample_counter = 1

    for idx in range(min_control_len):
        row = {
            translations[language_code]["sample_number"]: sample_counter,
            translations[language_code]["target_gene"]: f"{target_gene} {i+1}",
            "Grup": translations[language_code]["control_group"],
            translations[language_code]["target_ct"]: control_target_ct_values[idx],
            translations[language_code]["reference_ct"]: round(ctrl_norm_factor[idx], 4),
            translations[language_code]["delta_ct_control"]: round(control_delta_ct[idx], 4),
            "Outlier Excluded": "No"
        }
        if num_ref_genes > 1:
            for r, arr in enumerate(ctrl_ref_arrays):
                row[f"Ref Gene {r+1} Ct"] = arr[idx]
        input_values_table.append(row)
        sample_counter += 1

    # Log excluded outliers as separate flagged rows
    for ex_idx in ctrl_excluded_target:
        input_values_table.append({
            translations[language_code]["sample_number"]: f"{ex_idx + 1} ⚠️",
            translations[language_code]["target_gene"]: f"{target_gene} {i+1}",
            "Grup": translations[language_code]["control_group"],
            translations[language_code]["target_ct"]: "EXCLUDED",
            translations[language_code]["reference_ct"]: "EXCLUDED",
            translations[language_code]["delta_ct_control"]: "EXCLUDED",
            "Outlier Excluded": f"Yes ({outlier_method})"
        })

    for j in range(num_patient_groups):
        st.markdown(
            f"<h4>{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['target_gene']} {i+1}</h4>",
            unsafe_allow_html=True
        )

        sample_target_ct = st.text_area(
            f"{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['target_gene']} {i+1} - {translations[language_code]['ct_value']}",
            key=f"sample_target_ct_{i}_{j}"
        )

        # ── Multi-reference gene input (Patient) ──────────────────────────────
        smp_ref_arrays = []
        all_smp_refs_valid = True

        for r in range(num_ref_genes):
            ref_label = f"Ref Gene {r+1}" if num_ref_genes > 1 else translations[language_code]["reference_gene"]
            smp_ref_ct_raw = st.text_area(
                f"{translations[language_code]['patient_group']} {j+1} — {ref_label} {i+1} — {translations[language_code]['ct_value']}",
                key=f"sample_reference_ct_{i}_{j}_{r}"
            )
            parsed = parse_input_data(smp_ref_ct_raw)
            if len(parsed) == 0:
                all_smp_refs_valid = False
            else:
                smp_ref_arrays.append(parsed)

        sample_target_ct_values = np.array(parse_input_data(sample_target_ct))

        if len(sample_target_ct_values) == 0 or not all_smp_refs_valid or len(smp_ref_arrays) == 0:
            st.error(translations[language_code]["warning_patient_ct"].format(j=j+1))
            continue

        min_sample_len = min(len(sample_target_ct_values), *[len(a) for a in smp_ref_arrays])
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        smp_ref_arrays = [a[:min_sample_len] for a in smp_ref_arrays]

        # ── Outlier detection — Patient Target Ct ─────────────────────────────
        smp_excluded_target = []  # always initialized
        if outlier_enabled and len(sample_target_ct_values) >= 3:
            detected_smp_tgt = detect_outliers_grubbs(sample_target_ct_values, alpha=grubbs_alpha) \
                               if outlier_method == "Grubbs" \
                               else detect_outliers_iqr(sample_target_ct_values, multiplier=iqr_multiplier)
            if detected_smp_tgt:
                sample_target_ct_values, smp_excluded_target = render_outlier_ui(
                    sample_target_ct_values,
                    f"{translations[language_code]['patient_group']} {j+1} — Target Gene {i+1}",
                    f"smp_tgt_{i}_{j}",
                    outlier_method
                )
                if smp_excluded_target:
                    keep_indices_smp = [k for k in range(min_sample_len) if k not in smp_excluded_target]
                    smp_ref_arrays = [a[keep_indices_smp] for a in smp_ref_arrays]
                    min_sample_len = len(keep_indices_smp)

        # ── geNorm + CV stability (Patient, shown when ≥2 ref genes) ─────────
        if num_ref_genes >= 2:
            smp_ref_matrix = np.vstack(smp_ref_arrays)
            smp_m_values   = compute_genorm_m(smp_ref_matrix)
            smp_cv_values  = [compute_cv(a) for a in smp_ref_arrays]

            unstable_smp   = [r for r, m in enumerate(smp_m_values) if m >= 1.0]
            borderline_smp = [r for r, m in enumerate(smp_m_values) if 0.5 <= m < 1.0]

            st.markdown(f"##### 📊 Reference Gene Stability — {translations[language_code]['patient_group']} {j+1}")
            smp_stab_cols = st.columns(num_ref_genes)
            for r, col in enumerate(smp_stab_cols):
                m_ok = smp_m_values[r] < 1.0
                cv_ok = smp_cv_values[r] < 5.0
                with col:
                    st.metric(
                        label=f"Ref Gene {r+1}",
                        value=f"M = {smp_m_values[r]:.3f}",
                        delta=f"CV = {smp_cv_values[r]:.2f}%"
                    )
                    if m_ok and cv_ok:
                        st.caption("✅ Stable")
                    elif m_ok or cv_ok:
                        st.caption("⚠️ Borderline")
                    else:
                        st.caption("❌ Unstable — M ≥ 1.0")

            # Stability bar chart (patient)
            fig_stab_smp = go.Figure()
            fig_stab_smp.add_trace(go.Bar(
                name="geNorm M-value",
                x=[f"Ref {r+1}" for r in range(num_ref_genes)],
                y=smp_m_values,
                marker_color=["#2ecc71" if m < 0.5 else "#f39c12" if m < 1.0 else "#e74c3c" for m in smp_m_values],
                text=[f"{m:.3f}" for m in smp_m_values],
                textposition="outside"
            ))
            fig_stab_smp.add_hline(y=0.5, line_dash="dot", line_color="green",
                               annotation_text="M=0.5 (strict)", annotation_position="right")
            fig_stab_smp.add_hline(y=1.0, line_dash="dash", line_color="orange",
                               annotation_text="M=1.0 (acceptable)", annotation_position="right")
            fig_stab_smp.update_layout(
                title=f"geNorm M-value — {translations[language_code]['patient_group']} {j+1} Reference Genes",
                yaxis_title="M-value (lower = more stable)",
                height=280
            )
            st.plotly_chart(fig_stab_smp, use_container_width=True)

            # ── Stability warnings (patient) ──────────────────────────────────
            if unstable_smp:
                unstable_names = ", ".join([f"Ref Gene {r+1}" for r in unstable_smp])
                st.warning(
                    f"⚠️ **Unstable reference gene(s) detected in "
                    f"{translations[language_code]['patient_group']} {j+1}: {unstable_names}**\n\n"
                    f"geNorm M-value ≥ 1.0 indicates considerable expression variability across "
                    f"samples in this group, which may compromise normalization reliability.\n\n"
                    f"**Analysis will continue**, but interpret results with caution.\n\n"
                    f"**Recommendations:**\n"
                    f"- Check for sample-to-sample variation, outliers, or data entry errors\n"
                    f"- Validate {unstable_names} in this sample group before drawing conclusions\n"
                    f"- A mismatch between control and patient group stability may itself indicate "
                    f"a biological or technical difference worth investigating\n"
                    f"- Consider replacing {unstable_names} with a validated, tissue-appropriate "
                    f"reference gene (e.g. from literature or HouseKeeper database)"
                )
            elif borderline_smp:
                borderline_names = ", ".join([f"Ref Gene {r+1}" for r in borderline_smp])
                st.info(
                    f"ℹ️ **Borderline stability in "
                    f"{translations[language_code]['patient_group']} {j+1}: {borderline_names}** (M = 0.5–1.0)\n\n"
                    f"Stability is within MIQE acceptable range. Consider adding a third reference "
                    f"gene to confirm robustness of normalization."
                )
            else:
                st.success(
                    f"✅ All reference genes in "
                    f"{translations[language_code]['patient_group']} {j+1} are stable (M < 0.5)."
                )

        # ── Normalization factor & ΔCt ────────────────────────────────────────
        # Re-sync lengths after any outlier removal
        min_sample_len = min(len(sample_target_ct_values), *[len(a) for a in smp_ref_arrays])
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        smp_ref_arrays = [a[:min_sample_len] for a in smp_ref_arrays]

        smp_norm_factor = geometric_mean_ct(smp_ref_arrays)
        sample_delta_ct = sample_target_ct_values - smp_norm_factor
        sample_reference_ct_values = smp_ref_arrays[0]

        average_sample_delta_ct = np.mean(sample_delta_ct) if len(sample_delta_ct) > 0 else None

        sample_counter = 1
        for idx in range(min_sample_len):
            row = {
                translations[language_code]["sample_number"]: sample_counter,
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                "Grup": f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["target_ct"]: sample_target_ct_values[idx],
                translations[language_code]["reference_ct"]: round(smp_norm_factor[idx], 4),
                translations[language_code]["delta_ct_patient"]: round(sample_delta_ct[idx], 4),
                "Outlier Excluded": "No"
            }
            if num_ref_genes > 1:
                for r, arr in enumerate(smp_ref_arrays):
                    row[f"Ref Gene {r+1} Ct"] = arr[idx]
            input_values_table.append(row)
            sample_counter += 1

        # Log excluded outliers as flagged rows
        for ex_idx in smp_excluded_target:
            input_values_table.append({
                translations[language_code]["sample_number"]: f"{ex_idx + 1} ⚠️",
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                "Grup": f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["target_ct"]: "EXCLUDED",
                translations[language_code]["reference_ct"]: "EXCLUDED",
                translations[language_code]["delta_ct_patient"]: "EXCLUDED",
                "Outlier Excluded": f"Yes ({outlier_method})"
            })

        # ΔΔCt ve Gen Ekspresyon Değişimi Hesaplama
        if average_control_delta_ct is not None and average_sample_delta_ct is not None:
            delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
            expression_change = 2 ** (-delta_delta_ct)

            # ── Pfaffl Calculation ──────────────────────────────────────────
            eff = gene_efficiencies.get(i, {"target_E": 2.0, "ref_E": 2.0})
            E_target = eff["target_E"]
            E_ref = eff["ref_E"]

            avg_ctrl_target = np.mean(control_target_ct_values)
            avg_ctrl_ref    = np.mean(ctrl_norm_factor)
            avg_smp_target  = np.mean(sample_target_ct_values)
            avg_smp_ref     = np.mean(smp_norm_factor)

            delta_ct_target_pfaffl = avg_ctrl_target - avg_smp_target
            delta_ct_ref_pfaffl    = avg_ctrl_ref    - avg_smp_ref

            pfaffl_ratio = (E_target ** delta_ct_target_pfaffl) / (E_ref ** delta_ct_ref_pfaffl)
            # ────────────────────────────────────────────────────────────────
            
            if expression_change == 1:
                regulation_status = translations[language_code]["no_change"]
            elif expression_change > 1:
                regulation_status = translations[language_code]["upregulated"]
            else:
                regulation_status = translations[language_code]["downregulated"]

            # Pfaffl regulation
            if pfaffl_ratio > 1:
                pfaffl_regulation = translations[language_code]["upregulated"]
            elif pfaffl_ratio < 1:
                pfaffl_regulation = translations[language_code]["downregulated"]
            else:
                pfaffl_regulation = translations[language_code]["no_change"]

            # ── Method comparison display ─────────────────────────────────
            st.markdown(f"#### {translations[language_code]['method_comparison']} — {translations[language_code]['target_gene']} {i+1} / {translations[language_code]['patient_group']} {j+1}")
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                st.metric(
                    label=translations[language_code]["classic_ddct"],
                    value=f"{expression_change:.4f}",
                    delta=regulation_status
                )
            with comp_col2:
                st.metric(
                    label=translations[language_code]["pfaffl_ratio"],
                    value=f"{pfaffl_ratio:.4f}",
                    delta=pfaffl_regulation
                )
            # ─────────────────────────────────────────────────────────────

            # ── Per-group pairwise stats (control vs this patient group) ────
            shapiro_control = stats.shapiro(control_delta_ct)
            shapiro_sample  = stats.shapiro(sample_delta_ct)
            levene_test     = stats.levene(control_delta_ct, sample_delta_ct)

            control_normal = shapiro_control.pvalue > 0.05
            sample_normal  = shapiro_sample.pvalue  > 0.05
            equal_variance = levene_test.pvalue     > 0.05

            if control_normal and sample_normal:
                if equal_variance:
                    test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct).pvalue
                    test_method = translations[language_code]["t_test"]
                else:
                    test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct, equal_var=False).pvalue
                    test_method = translations[language_code]["welch_t_test"]
                test_type = translations[language_code]["parametric"]
            else:
                test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct).pvalue
                test_method = translations[language_code]["mann_whitney_u_test"]
                test_type   = translations[language_code]["non_parametric"]

            significance = translations[language_code]["significant"] if test_pvalue < 0.05 \
                           else translations[language_code]["insignificant"]

            # ── Decision pathway display ──────────────────────────────────
            with st.expander(
                f"🔬 Statistical decision — {translations[language_code]['target_gene']} {i+1} / "
                f"{translations[language_code]['patient_group']} {j+1}",
                expanded=False
            ):
                st.markdown("**Step-by-step test selection:**")

                # Step 1 — Shapiro-Wilk
                sw_ctrl_sym = "✅" if control_normal else "❌"
                sw_smp_sym  = "✅" if sample_normal  else "❌"
                st.markdown(
                    f"**1. Shapiro-Wilk normality test**  \n"
                    f"- Control group: W={shapiro_control.statistic:.4f}, "
                    f"p={shapiro_control.pvalue:.4f} {sw_ctrl_sym} "
                    f"{'Normal' if control_normal else 'Non-normal'}  \n"
                    f"- {translations[language_code]['patient_group']} {j+1}: "
                    f"W={shapiro_sample.statistic:.4f}, "
                    f"p={shapiro_sample.pvalue:.4f} {sw_smp_sym} "
                    f"{'Normal' if sample_normal else 'Non-normal'}"
                )

                # Step 2 — Levene (only if both normal)
                if control_normal and sample_normal:
                    lev_sym = "✅" if equal_variance else "⚠️"
                    st.markdown(
                        f"**2. Levene variance homogeneity test**  \n"
                        f"- F={levene_test.statistic:.4f}, p={levene_test.pvalue:.4f} "
                        f"{lev_sym} {'Equal variances' if equal_variance else 'Unequal variances'}"
                    )
                else:
                    st.markdown(
                        "**2. Levene test** — *skipped* "
                        "(normality not met; non-parametric test will be used)"
                    )

                # Step 3 — Selected test
                if not control_normal or not sample_normal:
                    reason = "Non-normal distribution in one or both groups"
                    recommendation = "Mann-Whitney U test (non-parametric)"
                elif equal_variance:
                    reason = "Both groups normal + equal variances"
                    recommendation = "Independent samples t-test"
                else:
                    reason = "Both groups normal + unequal variances (Levene p < 0.05)"
                    recommendation = "Welch t-test (does not assume equal variances)"

                st.success(
                    f"**3. Selected test:** {test_method}  \n"
                    f"**Reason:** {reason}  \n"
                    f"**Result:** p = {test_pvalue:.4f} → **{significance}**"
                )

                if num_patient_groups >= 2:
                    st.caption(
                        "⚠️ Note: When ≥ 3 groups are present, see the "
                        "**Multi-Group Comparison** section below for ANOVA / "
                        "Kruskal-Wallis omnibus testing with post-hoc correction."
                    )
            # ─────────────────────────────────────────────────────────────

            stats_data.append({
                translations[language_code]["target_gene"]:   f"{translations[language_code]['target_gene']} {i+1}",
                translations[language_code]["patient_group"]: f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["test_type"]:     test_type,
                translations[language_code]["test_method"]:   test_method,
                translations[language_code]["test_pvalue"]:   test_pvalue,
                translations[language_code]["significance"]:  significance,
                "Comparison": f"Control vs {translations[language_code]['patient_group']} {j+1}"
            })

            data.append({
                translations[language_code]["target_gene"]:         f"{translations[language_code]['target_gene']} {i+1}",
                translations[language_code]["patient_group"]:       f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["delta_delta_ct"]:      delta_delta_ct,
                translations[language_code]["gene_expression_change"]: expression_change,
                translations[language_code]["pfaffl_ratio"]:        pfaffl_ratio,
                "E target":                                          round(E_target, 4),
                "E ref":                                             round(E_ref, 4),
                translations[language_code]["regulation_status"]:   regulation_status,
                translations[language_code]["delta_ct_control"]:    average_control_delta_ct,
                translations[language_code]["delta_ct_patient"]:    average_sample_delta_ct
            })

# ─── MULTI-GROUP ANALYSIS (3+ patient groups per target gene) ────────────────
# Collect all ΔCt arrays per target gene for omnibus testing
multigroup_results = []   # records for display / PDF

for i in range(num_target_genes):
    # Pull per-group ΔCt values from stats_data provenance via data dict
    # Re-derive from input_values_table (source of truth after outlier removal)
    gene_label = f"{translations[language_code]['target_gene']} {i+1}"

    ctrl_dct = [
        float(d[translations[language_code]["delta_ct_control"]])
        for d in input_values_table
        if d.get("Grup") == translations[language_code]["control_group"]
        and d.get(translations[language_code]["target_gene"]) == gene_label
        and d.get(translations[language_code]["delta_ct_control"]) not in ("EXCLUDED", None)
        and d.get("Outlier Excluded", "No") == "No"
    ]

    patient_dcts = {}
    for j in range(num_patient_groups):
        pg_label = f"{translations[language_code]['patient_group']} {j+1}"
        vals = [
            float(d[translations[language_code]["delta_ct_patient"]])
            for d in input_values_table
            if d.get("Grup") == pg_label
            and d.get(translations[language_code]["target_gene"]) == gene_label
            and d.get(translations[language_code]["delta_ct_patient"]) not in ("EXCLUDED", None)
            and d.get("Outlier Excluded", "No") == "No"
        ]
        if vals:
            patient_dcts[pg_label] = vals

    if not ctrl_dct or not patient_dcts:
        continue

    all_groups      = [ctrl_dct] + list(patient_dcts.values())
    all_group_names = [translations[language_code]["control_group"]] + list(patient_dcts.keys())
    n_groups        = len(all_groups)

    if n_groups < 3:
        # 2-group: already handled above — just note it
        multigroup_results.append({
            "gene": gene_label,
            "n_groups": n_groups,
            "note": "2-group comparison — pairwise test already reported above.",
            "omnibus_test": "—", "omnibus_p": None,
            "posthoc": [], "correction": "—"
        })
        continue

    # ── Omnibus test selection ────────────────────────────────────────────────
    normality_ok  = all(stats.shapiro(g).pvalue > 0.05 for g in all_groups if len(g) >= 3)
    levene_p      = stats.levene(*all_groups).pvalue if n_groups >= 2 else 1.0
    variance_ok   = levene_p > 0.05

    if normality_ok and variance_ok:
        omnibus_stat, omnibus_p = stats.f_oneway(*all_groups)
        omnibus_test  = "One-way ANOVA"
        omnibus_type  = "parametric"
        posthoc_method = "Tukey HSD"
    elif normality_ok and not variance_ok:
        # Welch ANOVA (scipy ≥ 1.11) — fallback to regular ANOVA if unavailable
        try:
            from scipy.stats import alexandergovern
            result = alexandergovern(*all_groups)
            omnibus_p    = result.pvalue
            omnibus_stat = result.statistic
        except Exception:
            omnibus_stat, omnibus_p = stats.f_oneway(*all_groups)
        omnibus_test   = "Welch ANOVA (unequal variances)"
        omnibus_type   = "parametric"
        posthoc_method = "Games-Howell (approx. via pairwise Welch t-test + FDR)"
    else:
        omnibus_stat, omnibus_p = stats.kruskal(*all_groups)
        omnibus_test   = "Kruskal-Wallis"
        omnibus_type   = "non-parametric"
        posthoc_method = "Dunn (pairwise Mann-Whitney U)"

    omnibus_sig = "Significant" if omnibus_p < 0.05 else "Not significant"

    # ── Post-hoc pairwise comparisons ────────────────────────────────────────
    pairs      = []
    raw_pvals  = []

    for a in range(n_groups):
        for b in range(a + 1, n_groups):
            g_a, g_b = all_groups[a], all_groups[b]
            if omnibus_type == "parametric" and variance_ok:
                p = stats.ttest_ind(g_a, g_b).pvalue
            elif omnibus_type == "parametric" and not variance_ok:
                p = stats.ttest_ind(g_a, g_b, equal_var=False).pvalue
            else:
                p = stats.mannwhitneyu(g_a, g_b, alternative="two-sided").pvalue
            pairs.append((all_group_names[a], all_group_names[b]))
            raw_pvals.append(p)

    # ── Multiple comparison correction ───────────────────────────────────────
    n_tests = len(raw_pvals)
    bonf_pvals = [min(p * n_tests, 1.0) for p in raw_pvals]

    # FDR Benjamini-Hochberg
    ranked     = sorted(range(n_tests), key=lambda k: raw_pvals[k])
    fdr_pvals  = [1.0] * n_tests
    for rank, idx in enumerate(ranked):
        fdr_pvals[idx] = min(raw_pvals[idx] * n_tests / (rank + 1), 1.0)
    # Enforce monotonicity
    for k in range(n_tests - 2, -1, -1):
        fdr_pvals[ranked[k]] = min(fdr_pvals[ranked[k]], fdr_pvals[ranked[k + 1]])

    posthoc_rows = []
    for idx, (pa, pb) in enumerate(pairs):
        posthoc_rows.append({
            "Comparison":        f"{pa} vs {pb}",
            "Raw p":             round(raw_pvals[idx], 4),
            "Bonferroni p":      round(bonf_pvals[idx], 4),
            "FDR p (B-H)":       round(fdr_pvals[idx], 4),
            "Sig (raw)":         "✅" if raw_pvals[idx]  < 0.05 else "—",
            "Sig (Bonferroni)":  "✅" if bonf_pvals[idx] < 0.05 else "—",
            "Sig (FDR)":         "✅" if fdr_pvals[idx]  < 0.05 else "—",
        })

    multigroup_results.append({
        "gene":          gene_label,
        "n_groups":      n_groups,
        "omnibus_test":  omnibus_test,
        "omnibus_type":  omnibus_type,
        "omnibus_p":     omnibus_p,
        "omnibus_sig":   omnibus_sig,
        "posthoc_method": posthoc_method,
        "posthoc_rows":  posthoc_rows,
        "normality_ok":  normality_ok,
        "variance_ok":   variance_ok,
        "note":          None
    })

# ── Display multi-group results ───────────────────────────────────────────────
if any(r["n_groups"] >= 3 for r in multigroup_results):
    st.markdown("---")
    st.markdown("## 📊 Multi-Group Comparison Analysis")

    with st.expander("ℹ️ About multi-group statistical analysis", expanded=False):
        st.markdown("""
**When is multi-group analysis applied?**  
Automatically activated when **≥ 3 groups** (control + 2 or more patient groups) are present for a target gene.  
This addresses the limitation of pairwise-only testing, which inflates Type I error when multiple comparisons are made without correction.

**Test selection logic (automatic):**

| Condition | Test |
|---|---|
| All groups normal + equal variances | One-way ANOVA → Tukey HSD |
| All groups normal + unequal variances | Welch ANOVA → Games-Howell |
| Any group non-normal | Kruskal-Wallis → Dunn (Mann-Whitney U) |

**Multiple comparison correction:**
- **Bonferroni**: conservative, controls family-wise error rate (FWER). Best when few comparisons.
- **FDR (Benjamini-Hochberg)**: controls false discovery rate. Better power for many comparisons.

**Recommendation:** Report both, discuss which is more appropriate for your study design.  
**Reference:** Dunn OJ. *J Am Stat Assoc* 1961; Benjamini & Hochberg. *J R Stat Soc B* 1995.
""")

    for res in multigroup_results:
        if res["n_groups"] < 3:
            continue

        st.markdown(f"### 🧬 {res['gene']} — {res['n_groups']} groups")

        # Decision pathway
        if res["normality_ok"] and res["variance_ok"]:
            decision_text = "✅ Normal distribution + equal variances → **One-way ANOVA + Tukey HSD**"
            decision_color = "success"
        elif res["normality_ok"] and not res["variance_ok"]:
            decision_text = "⚠️ Normal distribution + **unequal variances** → **Welch ANOVA + Games-Howell**"
            decision_color = "warning"
        else:
            decision_text = "⚠️ **Non-normal distribution** → **Kruskal-Wallis + Dunn post-hoc**"
            decision_color = "warning"

        if decision_color == "success":
            st.success(decision_text)
        else:
            st.warning(decision_text)

        # Omnibus result
        omni_col1, omni_col2, omni_col3 = st.columns(3)
        omni_col1.metric("Omnibus Test", res["omnibus_test"])
        omni_col2.metric("p-value", f"{res['omnibus_p']:.4f}")
        omni_col3.metric("Result", res["omnibus_sig"])

        if res["omnibus_p"] >= 0.05:
            st.info(
                "ℹ️ Omnibus test is **not significant** (p ≥ 0.05). "
                "Post-hoc comparisons are shown for completeness but should be interpreted with caution — "
                "no overall group effect was detected."
            )

        # Post-hoc table
        st.markdown(f"**Post-hoc: {res['posthoc_method']}** with Bonferroni & FDR correction")
        ph_df = pd.DataFrame(res["posthoc_rows"])
        st.dataframe(ph_df, use_container_width=True)

        # Visualise adjusted p-values
        fig_ph = go.Figure()
        comparisons = [r["Comparison"] for r in res["posthoc_rows"]]
        fig_ph.add_trace(go.Bar(
            name="Raw p", x=comparisons,
            y=[r["Raw p"] for r in res["posthoc_rows"]],
            marker_color="#4C72B0"
        ))
        fig_ph.add_trace(go.Bar(
            name="Bonferroni p", x=comparisons,
            y=[r["Bonferroni p"] for r in res["posthoc_rows"]],
            marker_color="#DD8452"
        ))
        fig_ph.add_trace(go.Bar(
            name="FDR p (B-H)", x=comparisons,
            y=[r["FDR p (B-H)"] for r in res["posthoc_rows"]],
            marker_color="#55A868"
        ))
        fig_ph.add_hline(y=0.05, line_dash="dash", line_color="red",
                         annotation_text="α = 0.05", annotation_position="right")
        fig_ph.update_layout(
            barmode="group",
            title=f"{res['gene']} — Post-hoc p-values (raw, Bonferroni, FDR)",
            yaxis_title="p-value",
            height=350
        )
        st.plotly_chart(fig_ph, use_container_width=True)

        # Download post-hoc CSV
        ph_csv = ph_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Download post-hoc results — {res['gene']}",
            data=ph_csv,
            file_name=f"posthoc_{res['gene'].replace(' ', '_')}.csv",
            mime="text/csv",
            key=f"ph_dl_{res['gene']}"
        )

elif num_patient_groups >= 2 and multigroup_results:
    # 2 groups present but no 3+ — show explicit limitation note
    st.markdown("---")
    st.info(
        "ℹ️ **Multi-group analysis not applicable:** Only 2 groups detected (Control + 1 patient group). "
        "Pairwise statistics are reported above. "
        "If your experiment includes 3 or more groups, increase the number of patient groups to enable "
        "automatic ANOVA / Kruskal-Wallis testing with post-hoc correction."
    )
# ─────────────────────────────────────────────────────────────────────────────

# Giriş Verileri Tablosunu Göster
if input_values_table: 
    st.subheader(f" {translations[language_code]['gr_tbl']}")
    input_df = pd.DataFrame(input_values_table) 
    st.write(input_df) 

    csv = input_df.to_csv(index=False).encode("utf-8")  
    st.download_button(
        label=translations[language_code]['download_csv'],
        data=csv, file_name="giris_verileri.csv", mime="text/csv") 

# Sonuçlar Tablosunu Göster
if data:
    st.subheader(f" {translations[language_code]['nil_mine']}")
    df = pd.DataFrame(data)
    st.write(df)

# İstatistik Sonuçları
if stats_data:
    st.subheader(f" {translations[language_code]['statistical_results']}")
    stats_df = pd.DataFrame(stats_data)
    st.write(stats_df)
    
    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=translations[language_code]['download_csv'],
        data=csv_stats,
        file_name="istatistik_sonuclari.csv",
        mime="text/csv")

# Grafik oluşturma
for i in range(num_target_genes):
    st.subheader(f"{translations[language_code]['target_gene']} {i+1} - {translations[language_code]['distribution_graph']}")

    control_target_ct_values = [
        d[translations[language_code]["target_ct"]] 
        for d in input_values_table
        if d["Grup"] == translations[language_code]["control_group"] and
           d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}" and
           d.get(translations[language_code]["target_ct"]) not in ("EXCLUDED", None) and
           d.get("Outlier Excluded", "No") == "No"
    ]

    control_reference_ct_values = [
        d[translations[language_code]["reference_ct"]] 
        for d in input_values_table
        if d["Grup"] == translations[language_code]["control_group"] and
           d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}" and
           d.get(translations[language_code]["reference_ct"]) not in ("EXCLUDED", None) and
           d.get("Outlier Excluded", "No") == "No"
    ]

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f" {translations[language_code]['error_missing_control_data'].format(i=i+1)}")
        continue

    control_delta_ct = np.array(control_target_ct_values, dtype=float) - np.array(control_reference_ct_values, dtype=float)
    average_control_delta_ct = np.mean(control_delta_ct)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0.8, 1.2],  
        y=[average_control_delta_ct, average_control_delta_ct],  
        mode='lines',
        line=dict(color='black', width=4),
        name=translations[language_code]["control_group_avg"]
    ))

    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            float(d[translations[language_code]["delta_ct_patient"]])
            for d in input_values_table 
            if d["Grup"] == f"{translations[language_code]['patient_group']} {j+1}" and 
               d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}" and
               d.get(translations[language_code]["delta_ct_patient"]) not in ("EXCLUDED", None) and
               d.get("Outlier Excluded", "No") == "No"
        ]

        if not sample_delta_ct_values:
            continue  

        average_sample_delta_ct = np.mean(sample_delta_ct_values)
        fig.add_trace(go.Scatter(
            x=[(j + 1.8), (j + 2.2)],  
            y=[average_sample_delta_ct, average_sample_delta_ct],  
            mode='lines',
            line=dict(color='black', width=4),
            name=f"{translations[language_code]['patient_group']} {j+1} {translations[language_code]['avg']}"
        ))

    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',  
        name=translations[language_code]["control_group"],
        marker=dict(color='blue'),
        text=[f"{translations[language_code]['control']} {value:.2f}, {translations[language_code]['sample']} {idx+1}" for idx, value in enumerate(control_delta_ct)],
        hoverinfo='text'
    ))

    for j in range(num_patient_groups):
        sample_delta_ct_values = [
            float(d[translations[language_code]["delta_ct_patient"]])
            for d in input_values_table 
            if d["Grup"] == f"{translations[language_code]['patient_group']} {j+1}" and 
               d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}" and
               d.get(translations[language_code]["delta_ct_patient"]) not in ("EXCLUDED", None) and
               d.get("Outlier Excluded", "No") == "No"
        ]

        if not sample_delta_ct_values:
            continue  

        fig.add_trace(go.Scatter(
            x=np.ones(len(sample_delta_ct_values)) * (j + 2) + np.random.uniform(-0.05, 0.05, len(sample_delta_ct_values)),
            y=sample_delta_ct_values,
            mode='markers',  
            name=f"{translations[language_code]['patient_group']} {j+1}",
            marker=dict(color='red'),
            text=[f"{translations[language_code]['patient']} {value:.2f}, {translations[language_code]['sample']} {idx+1}" for idx, value in enumerate(sample_delta_ct_values)],
            hoverinfo='text'
        ))

    fig.update_layout(
        title=f"{translations[language_code]['target_gene']} {i+1} - {translations[language_code]['delta_ct_distribution']}",
        xaxis=dict(
            tickvals=[1] + [j + 2 for j in range(num_patient_groups)],
            ticktext=[translations[language_code]['control_group']] + [f"{translations[language_code]['patient_group']} {j+1}" for j in range(num_patient_groups)],
            title=translations[language_code]['x_axis_title']
        ),
        yaxis=dict(title=translations[language_code]['delta_ct_value']),
        showlegend=True
    )
    st.plotly_chart(fig)

# PDF rapor oluşturma kısmı
def get_font_path():
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
        '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
        '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    results = glob.glob('/usr/share/fonts/**/*.ttf', recursive=True)
    if results:
        return results[0]
    return None

font_path = get_font_path()
if font_path:
    try:
        pdfmetrics.registerFont(TTFont('CustomFont', font_path))
        REGISTERED_FONT = 'CustomFont'
    except Exception as e:
        st.warning(f"Font yüklenemedi: {e}. Varsayılan font kullanılıyor.")
        REGISTERED_FONT = 'Helvetica'
else:
    REGISTERED_FONT = 'Helvetica'

def create_pdf(results, stats, input_df, language_code):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    font_name = REGISTERED_FONT
    styles['Normal'].fontName = font_name
    styles['Title'].fontName = font_name
    styles['Heading2'].fontName = font_name

    elements.append(Paragraph(translations[language_code]["report_title"], styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(translations[language_code]["input_data_table"], styles['Heading2']))
    
    table_data = [input_df.columns.tolist()] + input_df.values.tolist()
    col_width = (letter[0] - 80) / len(input_df.columns)
    table = Table(table_data, colWidths=[col_width] * len(input_df.columns))
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Efficiency section in PDF
    elements.append(Paragraph(translations[language_code]["efficiency_header"], styles['Heading2']))
    elements.append(Spacer(1, 6))
    for i, eff in gene_efficiencies.items():
        e_target = eff["target_E"]
        e_ref = eff["ref_E"]
        t_pct = (e_target - 1) * 100
        r_pct = (e_ref - 1) * 100
        diff = abs(t_pct - r_pct)
        status = "✓ OK" if diff <= efficiency_threshold else "⚠ WARNING"
        eff_text = (
            f"{translations[language_code]['target_gene']} {i+1}: "
            f"E_target={e_target:.4f} ({t_pct:.1f}%), "
            f"E_ref={e_ref:.4f} ({r_pct:.1f}%), "
            f"Diff={diff:.1f}% — {status}"
        )
        elements.append(Paragraph(eff_text, styles['Normal']))
        elements.append(Spacer(1, 4))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(translations[language_code]["results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for result in results:
        classic = result.get(translations[language_code]['gene_expression_change'], 'N/A')
        pfaffl  = result.get(translations[language_code]['pfaffl_ratio'], 'N/A')
        classic_str = f"{classic:.4f}" if isinstance(classic, float) else str(classic)
        pfaffl_str  = f"{pfaffl:.4f}"  if isinstance(pfaffl, float) else str(pfaffl)
        text = (
            f"{result[translations[language_code]['target_gene']]} - "
            f"{result[translations[language_code]['patient_group']]} | "
            f"ΔΔCt: {result[translations[language_code]['delta_delta_ct']]:.2f} | "
            f"2^(-ΔΔCt): {classic_str} | "
            f"Pfaffl: {pfaffl_str} | "
            f"{result[translations[language_code]['regulation_status']]}"
        )
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    elements.append(Paragraph(translations[language_code]["statistical_results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for stat in stats:
        text = (f"{stat[translations[language_code]['target_gene']]} - {stat[translations[language_code]['patient_group']]} | "
                f"{translations[language_code]['test_method']}: {stat[translations[language_code]['test_method']]} | "
                f"p: {stat[translations[language_code]['test_pvalue']]:.4f} | {stat[translations[language_code]['significance']]}")
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    elements.append(Paragraph(translations[language_code]["statistical_evaluation"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    explanation = translations[language_code]["statistical_explanation"]
    
    for line in explanation.split(". "):
        elements.append(Paragraph(line.strip() + '.', styles['Normal']))
        elements.append(Spacer(1, 6))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button(f"📥 {translations[language_code]['generate_pdf']}"):
    if input_values_table:
        pdf_buffer = create_pdf(data, stats_data, pd.DataFrame(input_values_table), language_code)
        st.download_button(label=f"{translations[language_code]['pdf_report']}", data=pdf_buffer, file_name="gen_ekspresyon_raporu.pdf", mime="application/pdf")
    else:
        st.error(translations[language_code]["error_no_data"])

st.markdown(f"<h4 style='font-size: 12px; font-family: Arial, sans-serif; color: #555;'><a href='mailto:mailtoburhanettin@gmail.com' style='color: #555; text-decoration: none;'>{translations[language_code]['subtitle']}</a></h4>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "### 💻 Desktop Application",
    unsafe_allow_html=False
)
st.sidebar.link_button(
    "⬇️ Download Desktop App",
    "https://drive.google.com/file/d/1oGBPqLeS6JxWBdVSs47qgEfl0wiMI3Z9/view?usp=sharing",
    use_container_width=True
)
