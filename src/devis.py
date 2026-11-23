"""Génération du devis : quantités, prix unitaires et total."""
import csv
import json
import os
from charges import charger_projet, descente_de_charges
from predimensionnement import cote_semelle

def charger_materiaux(chemin):
   """Lit materiaux.json (désignation, unité, prix unitaire par matériau)."""
   try:
       with open(chemin, encoding="utf-8") as fichier:
           return json.load(fichier)
   except FileNotFoundError:
       raise FileNotFoundError("Fichier introuvable : " + chemin)

def lire_bordereau(chemin):
   """Lit bordereau.csv : liste de (désignation, matériau, quantité)."""
   lignes = []
   try:
       with open(chemin, encoding="utf-8-sig", newline="") as fichier:
           for ligne in csv.DictReader(fichier):
               lignes.append((ligne["designation"], ligne["materiau"],
                              float(ligne["quantite"])))
   except FileNotFoundError:
       raise FileNotFoundError("Fichier introuvable : " + chemin)
   except (KeyError, ValueError) as erreur:
       raise ValueError("Bordereau invalide : " + str(erreur))
   return lignes

def quantites_structure(projet):
   """Retourne (volume de béton en m³, masse d'acier en kg) de la structure."""
   tx = projet["grille"]["travees_x_m"]
   ty = projet["grille"]["travees_y_m"]
   niveaux = projet["niveaux"]
   nb = niveaux["nombre"]
   nx, ny = len(tx) + 1, len(ty) + 1   # nombre de files de poteaux
   v_dalles = sum(tx) * sum(ty) * projet["plancher"]["epaisseur_dalle_m"] * nb
   poteau = projet["poteaux"]
   v_poteaux = (nx * ny * poteau["b_m"] * poteau["h_m"]
                * niveaux["hauteur_etage_m"] * nb)
   nombres = {"Angle": 4,
              "Rive": 2 * (nx - 2) + 2 * (ny - 2),
              "Central": (nx - 2) * (ny - 2)}
   charges = descente_de_charges(projet)
   h_semelle = projet["semelles"]["hauteur_m"]
   v_semelles = sum(nombres[t] * cote_semelle(charges[t]["G+Q"]) ** 2
                    * h_semelle for t in nombres)
   ratios = projet["ratios_acier_kg_m3"]
   acier = (v_dalles * ratios["dalles"] + v_poteaux * ratios["poteaux"]
            + v_semelles * ratios["semelles"])
   return v_dalles + v_poteaux + v_semelles, acier

def generer_devis(chemin_projet, chemin_materiaux, chemin_bordereau):
   """Retourne (lignes chiffrées, lignes non chiffrées, total)."""
   projet = charger_projet(chemin_projet)
   materiaux = charger_materiaux(chemin_materiaux)
   try:
       beton, acier = quantites_structure(projet)
   except (KeyError, IndexError) as erreur:
       raise ValueError("Donnée manquante dans projet.json : " + str(erreur))
   lignes = [("Béton de la structure", "beton_C25_30", beton),
             ("Acier de la structure", "acier_HA500", acier)]
   lignes += lire_bordereau(chemin_bordereau)
   chiffrees, non_chiffrees, total = [], [], 0.0
   for designation, cle, quantite in lignes:
       materiau = materiaux.get(cle)
       if materiau is None:   # matériau absent : on le signale sans planter
           non_chiffrees.append((designation, cle, quantite))
           continue
       montant = quantite * materiau["prix_unitaire"]
       chiffrees.append((designation, materiau["unite"], round(quantite, 2),
                         materiau["prix_unitaire"], round(montant)))
       total += montant
   return chiffrees, non_chiffrees, round(total)

def afficher_devis(chiffrees, non_chiffrees, total):
   """Affiche le devis sous forme de tableau."""
   modele = "{:<34}{:>6}{:>12}{:>12}{:>14}"
   print(modele.format("Désignation", "Unité", "Quantité", "P.U.", "Montant"))
   for ligne in chiffrees:
       print(modele.format(*ligne))
   print("TOTAL :", total, "FCFA")
   for designation, cle, quantite in non_chiffrees:
       print("Non chiffré (absent de materiaux.json) :", designation,
             "[" + cle + "]", quantite)

if __name__ == "__main__":
   dossier = os.path.join(os.path.dirname(__file__), "..", "donnees")
   afficher_devis(*generer_devis(os.path.join(dossier, "projet.json"),
                                 os.path.join(dossier, "materiaux.json"),
                                 os.path.join(dossier, "bordereau.csv")))