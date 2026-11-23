"""Tests de la descente de charges (valeurs de contrôle de la slide)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from charges import charger_projet, descente_de_charges
CHEMIN = os.path.join(os.path.dirname(__file__), "..", "donnees", "projet.json")

def test_descente():
   r = descente_de_charges(charger_projet(CHEMIN))
   assert (r["Angle"]["G+Q"], r["Angle"]["N_ELU"]) == (122.1, 168.4)
   assert (r["Rive"]["G+Q"], r["Rive"]["N_ELU"]) == (230.1, 317.8)
   assert (r["Central"]["G+Q"], r["Central"]["N_ELU"]) == (446.1, 616.6)

if __name__ == "__main__":
   test_descente()
   print("Tous les tests passent.")