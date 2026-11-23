"""Descente de charges : G, Q, G+Q (service) et N_ELU par type de poteau."""
import json
COEF_G = 1.35   # coefficient sur les charges permanentes (ELU)
COEF_Q = 1.5    # coefficient sur les charges d'exploitation (ELU)

def charger_projet(chemin):
   """Lit le fichier JSON du projet et retourne un dictionnaire."""
   try:
       with open(chemin, encoding="utf-8") as fichier:
           return json.load(fichier)
   except FileNotFoundError:
       raise FileNotFoundError("Fichier projet introuvable : " + chemin)
   except json.JSONDecodeError as erreur:
       raise ValueError("Fichier JSON invalide : " + str(erreur))

def surfaces_influence(travees_x, travees_y):
   """Retourne la surface d'influence (m²) de chaque type de poteau."""
   fin_x, fin_y = travees_x[0] / 2, travees_y[0] / 2
   int_x = (travees_x[0] + travees_x[1]) / 2
   int_y = (travees_y[0] + travees_y[1]) / 2
   return {"Angle": fin_x * fin_y,
           "Rive": int_x * fin_y,
           "Central": int_x * int_y}

def descente_de_charges(projet):
   """Retourne {type: {"G", "Q", "G+Q", "N_ELU"}} pour Angle, Rive, Central."""
   try:
       gamma = projet["beton"]["poids_volumique_kn_m3"]
       niveaux = projet["niveaux"]
       nombre = niveaux["nombre"]
       q_par_niveau = niveaux["q_exploitation_kn_m2"]
       plancher = projet["plancher"]
       g_plancher = (plancher["epaisseur_dalle_m"] * gamma
                     + plancher["g_complementaire_kn_m2"])
       poteau = projet["poteaux"]
       poids_poteau = (poteau["b_m"] * poteau["h_m"] * gamma
                       * niveaux["hauteur_etage_m"])
       grille = projet["grille"]
       surfaces = surfaces_influence(grille["travees_x_m"],
                                     grille["travees_y_m"])
   except (KeyError, IndexError) as erreur:
       raise ValueError("Donnée manquante dans projet.json : " + str(erreur))
   if len(q_par_niveau) != nombre:
       raise ValueError("Il faut une charge Q par niveau.")
   resultat = {}
   for nom, surface in surfaces.items():
       g = nombre * (g_plancher * surface + poids_poteau)
       q = sum(q_par_niveau) * surface
       resultat[nom] = {"G": round(g, 2), "Q": round(q, 2),
                        "G+Q": round(g + q, 1),
                        "N_ELU": round(COEF_G * g + COEF_Q * q, 1)}
   return resultat