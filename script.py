import webbrowser
import time
import re
import pyautogui

# === CONSTANTES ===
FICHIER_SOURCE = 'Favorite Videos - Copie.txt'
URL_PATTERN = r'https?://[^\s]+'
TOLERANCE = 1
TIMEOUT = 15

POINTS_CLIC = [
    {"coord": (1509, 804), "couleur": (231, 231, 231)},  # #e7e7e7
    {"coord": (1510, 851), "couleur": (255, 255, 255)},  # #ffffff
]
COULEUR_STOP = (250, 206, 21)  # #face15

# === FONCTIONS UTILITAIRES ===

def couleur_proche(c1, c2, tolerance=TOLERANCE):
    """Retourne True si les couleurs sont proches selon la tolérance."""
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def extraire_liens(lignes, pattern=URL_PATTERN):
    """Extrait tous les liens d'une liste de lignes."""
    return [re.search(pattern, ligne).group() for ligne in lignes if re.search(pattern, ligne)]

def supprimer_lien_et_date(lignes, lien, pattern=URL_PATTERN):
    """Supprime la date (ligne précédente) et le lien du fichier."""
    nouvelles_lignes = []
    i = 0
    lien_supprime = False
    while i < len(lignes):
        if not lien_supprime and re.search(pattern, lignes[i]) and lien in lignes[i]:
            if i > 0:
                del nouvelles_lignes[-1]  # Supprimer la date déjà ajoutée
            lien_supprime = True
            i += 1  # Sauter la ligne du lien
        else:
            nouvelles_lignes.append(lignes[i])
        i += 1
    return nouvelles_lignes

def attendre_et_clic(timeout, points, couleur_stop):
    """Attend qu'un des points ait la bonne couleur, clique dessus, ou stoppe si couleur_stop détectée."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        screenshot = pyautogui.screenshot()
        for point in points:
            pixel_color = screenshot.getpixel(point["coord"])
            if couleur_proche(pixel_color, couleur_stop):
                print(f"Couleur d'arrêt détectée à {point['coord']}, fermeture immédiate.")
                return "stop"
            if couleur_proche(pixel_color, point["couleur"]):
                pyautogui.click(x=point["coord"][0], y=point["coord"][1])
                print(f"Clic effectué à {point['coord']} (proche de {point['couleur']}).")
                time.sleep(1)
                return "clicked"
        time.sleep(0.5)
    return "timeout"

def traiter_lien(lien, lignes):
    """Traite un lien : ferme l'onglet, ouvre le lien, attend/clic, supprime du fichier."""
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(1)
    pyautogui.moveTo(100, 100)
    webbrowser.open_new_tab(lien)
    print(f"Ouverture de : {lien}")
    time.sleep(0.2)

    resultat = attendre_et_clic(TIMEOUT, POINTS_CLIC, COULEUR_STOP)
    if resultat == "timeout":
        print("Aucun pixel correspondant après attente, pas de clic.")

    # Mise à jour du fichier
    nouvelles_lignes = supprimer_lien_et_date(lignes, lien)
    with open(FICHIER_SOURCE, 'w', encoding='utf-8') as f:
        f.writelines(nouvelles_lignes)
    print("Date et lien supprimés du fichier.\nOnglet fermé.")

    return nouvelles_lignes

# === SCRIPT PRINCIPAL ===

def main():
    with open(FICHIER_SOURCE, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    liens = extraire_liens(lignes)
    print(f"{len(liens)} liens trouvés. Début du traitement...")

    compteur = 0
    for lien in liens:
        lignes = traiter_lien(lien, lignes)
        compteur += 1
        print(f"Nombre de liens ajoutés/traités : {compteur}")

    print("Traitement terminé.")


if __name__ == "__main__":
    main()
