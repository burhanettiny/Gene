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

### 🔬 Amplification Efficiency
- Enter E value directly (e.g. 2.0 = 100%) or slope from standard curve  
- E = 10^(-1/slope)  
- Acceptable range: 90–110% (E between 1.8–2.2)  
- **Pfaffl method**: Ratio = (E_target^ΔCt_target) / (E_ref^ΔCt_ref)  

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
st.markdown(f"<h4>{translations[language_code]['efficiency_header']}</h4>", unsafe_allow_html=True)
st.info(translations[language_code]["efficiency_note"])

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
    key="eff_threshold"
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
                    key=f"target_slope_{i}"
                )
                target_E = 10 ** (-1.0 / target_slope) if target_slope != 0 else 2.0
                st.markdown(f"**E (target) = {target_E:.4f}** ({(target_E - 1) * 100:.1f}%)")
            else:
                target_E = st.number_input(
                    translations[language_code]["efficiency_target_label"].format(i=i+1),
                    min_value=1.0, max_value=3.0, value=2.0, step=0.01, format="%.4f",
                    key=f"target_E_{i}"
                )
                st.markdown(f"**{(target_E - 1) * 100:.1f}%**")

        with col2:
            if use_slope:
                ref_slope = st.number_input(
                    translations[language_code]["efficiency_ref_slope_label"].format(i=i+1),
                    value=-3.32, step=0.01, format="%.4f",
                    key=f"ref_slope_{i}"
                )
                ref_E = 10 ** (-1.0 / ref_slope) if ref_slope != 0 else 2.0
                st.markdown(f"**E (ref) = {ref_E:.4f}** ({(ref_E - 1) * 100:.1f}%)")
            else:
                ref_E = st.number_input(
                    translations[language_code]["efficiency_ref_label"].format(i=i+1),
                    min_value=1.0, max_value=3.0, value=2.0, step=0.01, format="%.4f",
                    key=f"ref_E_{i}"
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

    control_target_ct = st.text_area(f"{translations[language_code]['control_group']} {i+1} - {translations[language_code]['target_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"{translations[language_code]['control_group']} {i+1} - {translations[language_code]['reference_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"control_reference_ct_{i}")
   
    control_target_ct_values = np.array(parse_input_data(control_target_ct))
    control_reference_ct_values = np.array(parse_input_data(control_reference_ct))

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(translations[language_code]["warning_control_ct"].format(i=i+1))
        continue
    
    min_control_len = min(len(control_target_ct_values), len(control_reference_ct_values))
    control_target_ct_values = control_target_ct_values[:min_control_len]
    control_reference_ct_values = control_reference_ct_values[:min_control_len]
    control_delta_ct = control_target_ct_values - control_reference_ct_values

    average_control_delta_ct = np.mean(control_delta_ct) if len(control_delta_ct) > 0 else None
    sample_counter = 1
    
    for idx in range(min_control_len):
        input_values_table.append({
            translations[language_code]["sample_number"]: sample_counter,
            translations[language_code]["target_gene"]: f"{target_gene} {i+1}",
            "Grup": translations[language_code]["control_group"],
            translations[language_code]["target_ct"]: control_target_ct_values[idx],
            translations[language_code]["reference_ct"]: control_reference_ct_values[idx],  
            translations[language_code]["delta_ct_control"]: control_delta_ct[idx]
        })
        sample_counter += 1
 
    for j in range(num_patient_groups):
        st.markdown(
            f"<h4>{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['target_gene']} {i+1}</h4>",
            unsafe_allow_html=True
        )

        sample_target_ct = st.text_area(f"{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['target_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"sample_target_ct_{i}_{j}")
        sample_reference_ct = st.text_area(f"{translations[language_code]['patient_group']} {j+1} - {translations[language_code]['reference_gene']} {i+1} - {translations[language_code]['ct_value']}", key=f"sample_reference_ct_{i}_{j}")
        
        sample_target_ct_values = np.array(parse_input_data(sample_target_ct))
        sample_reference_ct_values = np.array(parse_input_data(sample_reference_ct))
         
        if len(sample_target_ct_values) == 0 or len(sample_reference_ct_values) == 0:
            st.error(translations[language_code]["warning_patient_ct"].format(j=j+1))
            continue
        
        min_sample_len = min(len(sample_target_ct_values), len(sample_reference_ct_values))
        sample_target_ct_values = sample_target_ct_values[:min_sample_len]
        sample_reference_ct_values = sample_reference_ct_values[:min_sample_len]
        sample_delta_ct = sample_target_ct_values - sample_reference_ct_values
        
        average_sample_delta_ct = np.mean(sample_delta_ct) if len(sample_delta_ct) > 0 else None
        
        sample_counter = 1  
        for idx in range(min_sample_len):
            input_values_table.append({
                translations[language_code]["sample_number"]: sample_counter,
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                "Grup": f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["target_ct"]: sample_target_ct_values[idx],
                translations[language_code]["reference_ct"]: sample_reference_ct_values[idx],
                translations[language_code]["delta_ct_patient"]: sample_delta_ct[idx]
            })
            sample_counter += 1
        
        # ΔΔCt ve Gen Ekspresyon Değişimi Hesaplama
        if average_control_delta_ct is not None and average_sample_delta_ct is not None:
            delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
            expression_change = 2 ** (-delta_delta_ct)

            # ── Pfaffl Calculation ──────────────────────────────────────────
            eff = gene_efficiencies.get(i, {"target_E": 2.0, "ref_E": 2.0})
            E_target = eff["target_E"]
            E_ref = eff["ref_E"]

            # Pfaffl: Ratio = (E_target ^ ΔCt_target) / (E_ref ^ ΔCt_ref)
            # ΔCt_target = mean_control_target - mean_sample_target (control vs sample direction)
            # ΔCt_ref    = mean_control_ref - mean_sample_ref
            avg_ctrl_target = np.mean(control_target_ct_values)
            avg_ctrl_ref    = np.mean(control_reference_ct_values)
            avg_smp_target  = np.mean(sample_target_ct_values)
            avg_smp_ref     = np.mean(sample_reference_ct_values)

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

            # İstatistiksel Testler
            shapiro_control = stats.shapiro(control_delta_ct)
            shapiro_sample = stats.shapiro(sample_delta_ct)
            levene_test = stats.levene(control_delta_ct, sample_delta_ct)
            
            control_normal = shapiro_control.pvalue > 0.05
            sample_normal = shapiro_sample.pvalue > 0.05
            equal_variance = levene_test.pvalue > 0.05
            
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
                test_type = translations[language_code]["non_parametric"]
               
            significance = translations[language_code]["significant"] if test_pvalue < 0.05 else translations[language_code]["insignificant"]
            
            stats_data.append({
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                translations[language_code]["patient_group"]: f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["test_type"]: test_type,
                translations[language_code]["test_method"]: test_method,
                translations[language_code]["test_pvalue"]: test_pvalue,
                translations[language_code]["significance"]: significance
            })
            
            data.append({
                translations[language_code]["target_gene"]: f"{translations[language_code]['target_gene']} {i+1}",
                translations[language_code]["patient_group"]: f"{translations[language_code]['patient_group']} {j+1}",
                translations[language_code]["delta_delta_ct"]: delta_delta_ct,
                translations[language_code]["gene_expression_change"]: expression_change,
                translations[language_code]["pfaffl_ratio"]: pfaffl_ratio,
                f"E target": round(E_target, 4),
                f"E ref": round(E_ref, 4),
                translations[language_code]["regulation_status"]: regulation_status,
                translations[language_code]["delta_ct_control"]: average_control_delta_ct,
                translations[language_code]["delta_ct_patient"]: average_sample_delta_ct
            })

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
           d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
    ]

    control_reference_ct_values = [
        d[translations[language_code]["reference_ct"]] 
        for d in input_values_table
        if d["Grup"] == translations[language_code]["control_group"] and
           d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
    ]

    if len(control_target_ct_values) == 0 or len(control_reference_ct_values) == 0:
        st.error(f" {translations[language_code]['error_missing_control_data'].format(i=i+1)}")
        continue

    control_delta_ct = np.array(control_target_ct_values) - np.array(control_reference_ct_values)
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
            d[translations[language_code]["delta_ct_patient"]] 
            for d in input_values_table 
            if d["Grup"] == f"{translations[language_code]['patient_group']} {j+1}" and 
               d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
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
            d[translations[language_code]["delta_ct_patient"]] 
            for d in input_values_table 
            if d["Grup"] == f"{translations[language_code]['patient_group']} {j+1}" and 
               d[translations[language_code]["target_gene"]] == f"{translations[language_code]['target_gene']} {i+1}"
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
