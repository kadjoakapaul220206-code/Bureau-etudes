"""Menu console du bureau d'études."""
import os
from contextlib import redirect_stdout
 
from charges import charger_projet, descente_de_charges
from devis import (afficher_devis, generer_devis, lire_bordereau,
                   quantites_structure)
from predimensionnement import cote_semelle, section_poteau
 
DOSSIER = os.path.join(os.path.dirname(__file__), "..", "donnees")
CHEMIN_PROJET = os.path.join(DOSSIER, "projet.json")
CHEMIN_MATERIAUX = os.path.join(DOSSIER, "materiaux.json")
CHEMIN_BORDEREAU = os.path.join(DOSSIER, "bordereau.csv")
 
MENU = """
--- Bureau d'études ---
1. Charger le projet (JSON)
2. Calculer le métré
3. Descente de charges
4. Prédimensionner poteaux et semelles
5. Générer le devis
6. Exporter un rapport
7. Calcul rapide (saisie manuelle)
8. Quitter"""
 
 
def saisir_nombre(message):
    """Demande un nombre positif à l'utilisateur, jusqu'à saisie valide."""
    while True:
        try:
            valeur = float(input(message).replace(",", "."))
            if valeur > 0:
                return valeur
            print("La valeur doit être positive.")
        except ValueError:
            print("Saisie invalide : entrez un nombre.")
 
 
def pause():
    """Laisse le temps de lire le résultat avant de réafficher le menu."""
    input("\nAppuyez sur Entrée pour revenir au menu...")
 
 
def charger():
    """Charge et vérifie un projet JSON. Retourne (projet, chemin)."""
    saisie = input("Fichier JSON (Entrée = fichier par défaut) : ").strip()
    chemin = saisie.strip('"') or CHEMIN_PROJET
    projet = charger_projet(chemin)
    descente_de_charges(projet)   # lève une erreur si des données manquent
    print("Projet chargé :", projet.get("nom", "sans nom"))
    return projet, chemin
 
 
def charger_par_defaut():
    """Charge donnees/projet.json sans rien demander."""
    projet = charger_projet(CHEMIN_PROJET)
    descente_de_charges(projet)
    return projet, CHEMIN_PROJET
 
 
def metre(projet):
    """Affiche les quantités : structure (béton, acier) et bordereau."""
    beton, acier = quantites_structure(projet)
    print("Béton de la structure :", round(beton, 2), "m3")
    print("Acier de la structure :", round(acier), "kg")
    for designation, _, quantite in lire_bordereau(CHEMIN_BORDEREAU):
        print(designation, ":", quantite)
 
 
def afficher_charges(projet):
    """Affiche la descente de charges de chaque type de poteau."""
    modele = "{:<9}{:>9}{:>9}{:>11}{:>12}"
    print(modele.format("Poteau", "G", "Q", "G+Q", "N_ELU"), "(kN)")
    for nom, r in descente_de_charges(projet).items():
        print(modele.format(nom, r["G"], r["Q"], r["G+Q"], r["N_ELU"]))
 
 
def predimensionner(projet):
    """Prédimensionne le poteau et la semelle de chaque type."""
    for nom, r in descente_de_charges(projet).items():
        a_min, calcule, retenu = section_poteau(r["N_ELU"])
        print(nom, "- poteau : A_min", a_min, "m2, côté", calcule,
              "cm -> retenu", retenu, "cm | semelle :",
              cote_semelle(r["G+Q"]), "m")
 
 
def devis(chemin_projet):
    """Génère et affiche le devis."""
    afficher_devis(*generer_devis(chemin_projet, CHEMIN_MATERIAUX,
                                  CHEMIN_BORDEREAU))
 
 
def exporter_rapport(projet, chemin_projet):
    """Écrit rapport.txt à la racine du projet."""
    chemin = os.path.join(os.path.dirname(__file__), "..", "rapport.txt")
    with open(chemin, "w", encoding="utf-8") as fichier:
        with redirect_stdout(fichier):
            print("RAPPORT -", projet.get("nom", ""))
            print("\n== Descente de charges ==")
            afficher_charges(projet)
            print("\n== Prédimensionnement ==")
            predimensionner(projet)
            print("\n== Devis ==")
            devis(chemin_projet)
    print("Rapport exporté :", os.path.abspath(chemin))
 
 
def calcul_rapide():
    """Prédimensionnement à partir de valeurs saisies au clavier."""
    g_plus_q = saisir_nombre("Charge G+Q en pied (kN) : ")
    print("Côté minimal de la semelle :", cote_semelle(g_plus_q), "m")
    n_elu = saisir_nombre("Effort N_ELU (kN) : ")
    a_min, calcule, retenu = section_poteau(n_elu)
    print("Poteau : A_min =", a_min, "m2, côté calculé =", calcule,
          "cm, côté retenu =", retenu, "cm")
 
 
def main():
    projet, chemin = None, CHEMIN_PROJET
    while True:
        print(MENU)
        choix = input("Votre choix : ").strip()
        if choix in ("8", "0"):
            print("Au revoir.")
            break
        if choix not in ("1", "2", "3", "4", "5", "6", "7"):
            print("Choix invalide : tapez un nombre entre 1 et 8.")
            pause()
            continue
        try:
            # Options 2 à 6 sans projet chargé : on charge le projet par défaut
            if choix in ("2", "3", "4", "5", "6") and projet is None:
                projet, chemin = charger_par_defaut()
            if choix == "1":
                projet, chemin = charger()
            elif choix == "2":
                metre(projet)
            elif choix == "3":
                afficher_charges(projet)
            elif choix == "4":
                predimensionner(projet)
            elif choix == "5":
                devis(chemin)
            elif choix == "6":
                exporter_rapport(projet, chemin)
            else:
                calcul_rapide()
        except (KeyError, IndexError, ValueError, FileNotFoundError) as erreur:
            print("Erreur :", erreur)
        pause()
 
 
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nAu revoir.")