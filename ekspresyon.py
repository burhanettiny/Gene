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

# Sidebar collapse görünür olması için CSS
st.markdown("""
<style>
[data-testid="stSidebarCollapseButton"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------
#   📘 Selectbox ALTINDA INSTRUCTION LINKİ
# --------------------------------------------
st.sidebar.markdown("---")
instruction_clicked = st.sidebar.button("📘 Instruction ")

# Instruction’a tıklanınca modal açılır
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

### 📈 Statistical Tests
- Shapiro–Wilk → checks normality  
- Levene → checks homogeneity of variances  
- Student’s t-test / Welch → compare means  
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
        "significance": "Anlamlılık",
        "target_gene": "Hedef Gen",
        "patient_group": "🩸 Hasta Grubu",
        "expression_change": "Gen Ekspresyon Değişimi",
        "regulation_status": "Regülasyon Durumu",
        "generate_pdf": "PDF Oluştur",
        "pdf_report": "Gen Ekspresyon Raporu",
        "error_no_data": "Veri bulunamadı, PDF oluşturulamadı.",
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
        "x_axis_title": "Grup Name",
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
        "reference_gene": "Reference Gen",
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
        "welch_t_test": "welch_t_test",
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
        "significance": "Significance",
        "target_gene": "Target Gene",
        "patient_group": "🩸 Patient Group",
        "expression_change": "Gene Expression Change",
        "regulation_status": "Regulation Status",
        "generate_pdf": "Generate PDF",
        "pdf_report": "Gene Expression Report",
        "error_no_data": "No data found, PDF could not be generated.",
        "statistical_explanation": (
            "During the statistical evaluation process, data distribution was analyzed using the Shapiro-Wilk test. "
            "If normality was met, variance homogeneity between groups was checked with Levene’s test. "
            "If variance was equal, an independent sample t-test was applied; otherwise, a Welch t-test was used. "
            "If normal distribution was not achieved, the non-parametric Mann-Whitney U test was applied. "
            "Significance was determined using the p < 0.05 criterion."
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
        "statistics": "Statistische Ergebnisse",
        "nil_mine": "📊 Ergebnisse",
        "gr_tbl": "📋 Eingabedaten Tabelle",
        "control_group": "🧬 Kontroll gruppe",
        "ctrl_trgt_ct": "🟦 Kontrollgruppe Zielgen {i} Ct-Werte",
        "ctrl_ref_ct": "🟦 Kontrollgruppe Referenz {i} Ct-Werte",
        "hst_trgt_ct": "🩸 Patientendaten gruppe Zielgen {j} Ct-Werte",
        "hst_ref_ct": "🩸 Patientendaten gruppe Referenz {j} Ct-Werte",
        "warning_control_ct": "⚠️ Achtung: Kontrollgruppe {i} Daten sollten untereinander eingegeben oder aus Excel ohne leere Zellen eingefügt werden.",
        "warning_patient_ct": "⚠️ Achtung: Geben Sie die Ct-Werte der Patientendaten gruppe untereinander ein oder kopieren Sie sie aus Excel ohne leere Zellen.",
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
        "welch_t_test": "welch_t_testi",
        "significant": "Signifikant",
        "insignificant": "Nicht signifikant",
        "test_type": "Testtyp",
        "test_method": "Verwendeter Test",
        "test_pvalue": "P-Wert",
        "significance": "Bedeutung",
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
        "significance": "Signifikanz",
        "target_gene": "Zielgen",
        "patient_group": "🩸 Patientengruppe",
        "expression_change": "Genexpressionsänderung",
        "regulation_status": "Regulierungsstatus",
        "generate_pdf": "PDF Erstellen",
        "pdf_report": "Genexpressionsbericht",
        "error_no_data": "Keine Daten gefunden, PDF konnte nicht erstellt werden.",
        "statistical_explanation": (
            "Während des statistischen Bewertungsprozesses wurde die Datenverteilung mit dem Shapiro-Wilk-Test analysiert. "
            "Wenn die Normalität erfüllt war, wurde die Varianzhomogenität zwischen den Gruppen mit dem Levene-Test überprüft. "
            "War die Varianz gleich, wurde ein unabhängiger Stichprobent-Test angewendet; andernfalls wurde ein Welch-T-Test verwendet. "
            "Wenn keine normale Verteilung vorlag, wurde der nicht-parametrische Mann-Whitney-U-Test angewendet. "
            "Die Signifikanz wurde anhand des Kriteriums p < 0,05 bestimmt."
            "Für Vorschläge und Unterstützung, Burhanettin Yalçinkaya - E-Mail: mailtoburhanettin@gmail.com"
        )
    },
    
    "fr": {
        "title": "🧬 GeneQuantify : Analyse de l’expression génique et des variations du nombre de copies (CNV)",
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
        "statistical_results": "📈 Résultats Statistiques",
        "download_csv": "📥 Télécharger CSV",
        "generate_pdf": "📥 Préparer le Rapport PDF",
        "pdf_report": "Rapport d'Analyse de l'Expression Génétique",
        "statistics": "Résultats Statistiques",
        "nil_mine": "📊 Résultats",
        "gr_tbl": "📋 Tableau des Données d'Entrée",
        "control_group": "🧬 Groupe Contrôle",
        "ctrl_trgt_ct": "🟦 Valeurs Ct du Gène Cible {i} pour le Groupe Contrôle",
        "ctrl_ref_ct": "🟦 Valeurs Ct du Gène Référence {i} pour le Groupe Contrôle",
        "hst_trgt_ct": "🩸 Valeurs Ct du Gène Cible {j} pour le Groupe Patient",
        "hst_ref_ct": "🩸 Valeurs Ct du Gène Référence {j} pour le Groupe Patient",
        "warning_control_ct": "⚠️ Avertissement : Les données du groupe témoin {i} doivent être saisies ligne par ligne ou copiées depuis Excel sans cellules vides.",
        "warning_patient_ct": "⚠️ Avertissement : Entrez les valeurs Ct du groupe patient ligne par ligne ou copiez-les depuis Excel sans cellules vides.",
        "statistical_results": "📈 Résultats Statistiques",
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
        "welch_t_test": "welch_t_test",
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
        "statistical_results": "Résultats Statistiques",
        "statistical_evaluation": "Évaluation Statistique",
        "significance": "Signification",
        "target_gene": "Gène Cible",
        "patient_group": "🩸 Groupe Patient",
        "expression_change": "Changement de l'Expression Génétique",
        "regulation_status": "Statut de Régulation",
        "generate_pdf": "Générer le PDF",
        "pdf_report": "Rapport sur l'Expression Génétique",
        "error_no_data": "Aucune donnée trouvée, le PDF n'a pas pu être généré.",
        "statistical_explanation": (
            "Au cours du processus d'évaluation statistique, la répartition des données a été analysée à l'aide du test de Shapiro-Wilk. "
            "Si la normalité était remplie, l'homogénéité de la variance entre les groupes a été vérifiée à l'aide du test de Levene. "
            "Si la variance était égale, un test t pour échantillons indépendants a été appliqué, sinon, un test t de Welch a été utilisé. "
            "Si aucune distribution normale n'était atteinte, le test non paramétrique de Mann-Whitney U a été appliqué. "
            "La signification a été déterminée en utilisant le critère p < 0,05."
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
        "statistical_results": "📈 Resultados Estadísticos",
        "download_csv": "📥 Descargar CSV",
        "generate_pdf": "📥 Preparar Informe en PDF",
        "pdf_report": "Informe de Análisis de Expresión Génica",
        "statistics": "Resultados Estadísticos",
        "nil_mine": "📊 Resultados",
        "gr_tbl": "📋 Tabla de Datos de Entrada",
        "control_group": "🧬 Grupo Control",
        "ctrl_trgt_ct": "🟦 Valores Ct del Gen Objetivo {i} para el Grupo Control",
        "ctrl_ref_ct": "🟦 Valores Ct del Gen de Referencia {i} para el Grupo Control",
        "hst_trgt_ct": "🩸 Valores Ct del Gen Objetivo {j} para el Grupo Paciente",
        "hst_ref_ct": "🩸 Valores Ct del Gen de Referencia {j} para el Grupo Paciente",
        "warning_control_ct": "⚠️ Advertencia: Los datos del grupo control {i} deben ingresarse fila por fila o copiarse desde Excel sin celdas vacías.",
        "warning_patient_ct": "⚠️ Advertencia: Ingrese los valores de Ct del grupo paciente fila por fila o cópielos desde Excel sin celdas vacías.",
        "statistical_results": "📈 Resultados Estadísticos",
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
        "welch_t_test": "welch_t_test",
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
        "statistical_results": "Resultados Estadísticos",
        "statistical_evaluation": "Evaluación Estadística",
        "significance": "Significación",
        "target_gene": "Gen Objetivo",
        "patient_group": "🩸 Grupo Paciente",
        "expression_change": "Cambio de Expresión Génica",
        "regulation_status": "Estado de Regulación",
        "generate_pdf": "Generar PDF",
        "pdf_report": "Informe de Expresión Génica",
        "error_no_data": "No se encontraron datos, no se pudo generar el PDF.",
        "statistical_explanation": (
            "Durante el proceso de evaluación estadística, se analizó la distribución de los datos mediante la prueba de Shapiro-Wilk. "
            "Si se cumplió la normalidad, se verificó la homogeneidad de varianza entre los grupos mediante la prueba de Levene. "
            "Si la varianza era igual, se aplicó la prueba t de muestras independientes; de lo contrario, se utilizó la prueba t de Welch. "
            "Si no se alcanzó una distribución normal, se aplicó la prueba no paramétrica Mann-Whitney U. "
            "La significancia se determinó utilizando el criterio p < 0.05."
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
        "statistical_results": "📈 النتائج الإحصائية",
        "download_csv": "📥 تحميل CSV",
        "generate_pdf": "📥 إعداد تقرير PDF",
        "pdf_report": "تقرير تحليل التعبير الجيني",
        "statistics": "النتائج الإحصائية",
        "nil_mine": "📊 النتائج",
        "gr_tbl": "📋 جدول بيانات الإدخال",
        "control_group": "🧬 مجموعة التحكم",
        "ctrl_trgt_ct": "🟦 قيم Ct الجين المستهدف {i} لمجموعة التحكم",
        "ctrl_ref_ct": "🟦 قيم Ct الجين المرجعي {i} لمجموعة التحكم",
        "hst_trgt_ct": "🩸 قيم Ct الجين المستهدف {j} لمجموعة المرضى",
        "hst_ref_ct": "🩸 قيم Ct الجين المرجعي {j} لمجموعة المرضى",
        "warning_control_ct": "⚠️ تحذير: يجب إدخال بيانات مجموعة التحكم {i} سطرًا بسطر أو نسخها من Excel دون خلايا فارغة.",
        "warning_patient_ct": "⚠️ تحذير: أدخل قيم Ct لمجموعة المرضى سطرًا بسطر أو انسخها من Excel دون خلايا فارغة.",
        "statistical_results": "📈 النتائج الإحصائية",
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
        "statistical_results": "النتائج الإحصائية",
        "statistical_evaluation": "التقييم الإحصائي",
        "significance": "الدلالة",
        "target_gene": "الجين المستهدف",
        "patient_group": "🩸 مجموعة المرضى",
        "expression_change": "تغيير التعبير الجيني",
        "regulation_status": "حالة التنظيم",
        "generate_pdf": "توليد تقرير PDF",
        "pdf_report": "تقرير التعبير الجيني",
        "error_no_data": "لم يتم العثور على بيانات، لم يتم إنشاء التقرير PDF.",
        "statistical_explanation": (
            "أثناء عملية التقييم الإحصائي، تم تحليل توزيع البيانات باستخدام اختبار شابيرو-ويلك. "
            "إذا تم تحقيق التوزيع الطبيعي، تم التحقق من تجانس التباين بين المجموعات باستخدام اختبار ليفين. "
            "إذا كانت التباين متساويًا، تم تطبيق اختبار t للعينة المستقلة، وإذا لم يكن كذلك، تم استخدام اختبار t ويلش. "
            "إذا لم يتم تحقيق التوزيع الطبيعي، تم تطبيق اختبار مان-ويتني U غير المعلمي. "
            "تم تحديد الدلالة باستخدام المعيار p < 0.05."
            "للاقتراحات والدعم، بورهانيتين يالجنكايا - البريد الإلكتروني: mailtoburhanettin@gmail.com"
        )
    }
}

                  
st.markdown(f"<h3>{translations[language_code]['title']}</h3>", unsafe_allow_html=True)
st.markdown(f"<h4>{translations[language_code]['patient_data_header']}</h4>", unsafe_allow_html=True)

num_target_genes = st.number_input(translations[language_code]["num_target_genes"], min_value=1, step=1, key="gene_count")
num_patient_groups = st.number_input(translations[language_code]["num_patient_groups"], min_value=1, step=1, key="patient_count")

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
    sample_counter = 1  # Kontrol grubu örnek sayacı
    
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
            
            if expression_change == 1:
                regulation_status = translations[language_code]["no_change"]
            elif expression_change > 1:
                regulation_status = translations[language_code]["upregulated"]
            else:
                regulation_status = translations[language_code]["downregulated"]
       
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
        label=translations[language_code]['download_csv'],  # Dil koduna göre etiket
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
        label=translations[language_code]['download_csv'],  # Dil koduna göre etiket
        data=csv_stats,
        file_name="istatistik_sonuclari.csv",
        mime="text/csv")

# Grafik oluşturma (her hedef gen için bir grafik oluşturulacak)
for i in range(num_target_genes):
    st.subheader(f"{translations[language_code]['target_gene']} {i+1} - {translations[language_code]['distribution_graph']}")

    # Kontrol Grubu Verileri
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

    # Grafik başlatma
    fig = go.Figure()

    # Kontrol Grubu Ortalama Çizgisi
    fig.add_trace(go.Scatter(
        x=[0.8, 1.2],  
        y=[average_control_delta_ct, average_control_delta_ct],  
        mode='lines',
        line=dict(color='black', width=4),
        name=translations[language_code]["control_group_avg"]
    ))

    # Hasta Gruplarının Ortalama Çizgileri
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

    # Veri Noktaları (Kontrol Grubu)
    fig.add_trace(go.Scatter(
        x=np.ones(len(control_delta_ct)) + np.random.uniform(-0.05, 0.05, len(control_delta_ct)),
        y=control_delta_ct,
        mode='markers',  
        name=translations[language_code]["control_group"],
        marker=dict(color='blue'),
        text=[f"{translations[language_code]['control']} {value:.2f}, {translations[language_code]['sample']} {idx+1}" for idx, value in enumerate(control_delta_ct)],
        hoverinfo='text'
    ))

    # Veri Noktaları (Hasta Grupları)
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

    # Grafik ayarları
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
import os
import glob

def get_font_path():
    # 1. Bilinen sistem yolları
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

    # 2. Sistemde .ttf ara
    results = glob.glob('/usr/share/fonts/**/*.ttf', recursive=True)
    if results:
        return results[0]

    return None  # Bulunamazsa Helvetica fallback

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
    font_name = REGISTERED_FONT  # ← sabit 'DejaVu' yerine dinamik
    styles['Normal'].fontName = font_name
    styles['Title'].fontName = font_name
    styles['Heading2'].fontName = font_name

    # Başlık
    elements.append(Paragraph(translations[language_code]["report_title"], styles['Title']))
    elements.append(Spacer(1, 12))

    # Giriş Verileri Tablosu Başlığı
    elements.append(Paragraph(translations[language_code]["input_data_table"], styles['Heading2']))
    
    # Tablo Verisi
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
    
    # Sonuçlar Başlığı
    elements.append(Paragraph(translations[language_code]["results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for result in results:
        text = (f"{result[translations[language_code]['target_gene']]} - {result[translations[language_code]['patient_group']]} | "
                f"ΔΔCt: {result[translations[language_code]['delta_delta_ct']]:.2f} | 2^(-ΔΔCt): {result[translations[language_code]['gene_expression_change']]:.2f} | "
                f"{result[translations[language_code]['regulation_status']]}")
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Sonuçlar
    elements.append(Paragraph(translations[language_code]["statistical_results"], styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for stat in stats:
        text = (f"{stat[translations[language_code]['target_gene']]} - {stat[translations[language_code]['patient_group']]} | "
                f"{translations[language_code]['test_method']}: {stat[translations[language_code]['test_method']]} | "
                f"p: {stat[translations[language_code]['test_pvalue']]:.4f} | {stat[translations[language_code]['significance']]}")
        elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 6))
    
    elements.append(PageBreak())
    
    # İstatistiksel Değerlendirme
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



