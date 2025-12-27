import pandas as pd
import os

# --- KONFIGURATION ---
FILE_PATH = r"C:\Users\Titan\Documents\TU-Darmstadt\2025_SoSe\MASTER THESIS\Quantitative DATA\Thesis_Results_Final_V5.csv"

# --- ANALYSE ---

print("Lade Daten...")

# 1. Daten laden und Spaltennamen ERZWINGEN
# Wir definieren die Namen manuell, falls sie in der CSV fehlen
column_names = ['Year', 'Company', 'Doc_Type', 'Sentence', 'Label', 'Score', 'Source']

try:
    # header=None bedeutet: "Lies alles als Daten". names=... setzt unsere Namen.
    df = pd.read_csv(FILE_PATH, header=None, names=column_names, on_bad_lines='skip')
    
    # Falls die CSV doch eine Header-Zeile hatte ("Year", "Company"...), steht die jetzt in Zeile 1.
    # Die müssen wir rausfiltern.
    df = df[df['Year'] != 'Year']
    
    # Datentypen korrigieren (Score zu Zahl machen)
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
    
    print(f"✅ Erfolgreich geladen: {len(df)} Sätze.")

except Exception as e:
    print(f"❌ Kritischer Fehler beim Laden: {e}")
    exit()

# 2. Filtern: Wir ignorieren "General corporate operations"
strategic_df = df[df['Label'] != 'general corporate operations'].copy()

print(f"-> Davon strategisch relevant (Pricing/Protection): {len(strategic_df)}")

if len(strategic_df) == 0:
    print("ACHTUNG: Keine strategischen Sätze gefunden. Überprüfe die Spalte 'Label' in der CSV manuell!")
    print("Beispiel Labels in deiner Datei:", df['Label'].unique()[:5])
    exit()

# 3. Pivot Table erstellen (Jahre x Firmen)
pivot = strategic_df.pivot_table(
    index=['Company', 'Year'], 
    columns='Label', 
    values='Sentence', 
    aggfunc='count', 
    fill_value=0
)

# Sicherstellen, dass beide Spalten da sind
required_cols = ['business model adaptation and pricing', 'coercive restriction and legal threat']
for col in required_cols:
    if col not in pivot.columns:
        pivot[col] = 0

# 4. Die "Coercive Intensity" berechnen
total = pivot[required_cols[0]] + pivot[required_cols[1]]
pivot['Total_Strategy_Mentions'] = total
pivot['Coercive_Share'] = (pivot['coercive restriction and legal threat'] / total).round(3)

# 5. Ergebnis anzeigen
print("\n--- ERGEBNIS TABELLE ---")
# Wir zeigen nur Spalten, die existieren, um Fehler zu vermeiden
cols_to_show = ['Total_Strategy_Mentions', 'Coercive_Share']
if 'coercive restriction and legal threat' in pivot.columns:
    cols_to_show.insert(0, 'coercive restriction and legal threat')

print(pivot[cols_to_show])

# Speichern
output_path = os.path.join(os.path.dirname(FILE_PATH), "Thesis_Aggregated_Results.xlsx")
pivot.to_excel(output_path)
print(f"\n✅ Aggregierte Daten gespeichert in: {output_path}")