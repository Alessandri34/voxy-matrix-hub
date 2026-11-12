"""La bande-son du film : musique et bruitages, entierement synthetises.

    python3 son.py          ->  sortie/son.wav   (48 kHz, stereo)

Aucun echantillon, aucune banque de sons : chaque note et chaque bruitage est
calcule ici. Deux raisons. Il n'y a donc **aucun droit a verifier** avant de
diffuser le film en publicite. Et le son se cale sur l'image au millieme :
les instants viennent de `reperes.json`, que `rendre.cjs` ecrit a partir de
la composition. On ne deplace jamais un bruitage a la main.

La musique est a 120 a la minute, en fa majeur : un temps toutes les 0,5 s,
une mesure toutes les 2 s. Les changements de plan tombent sur les mesures.

    0-6 s    re mineur, sans batterie      la question reste ouverte
    6-12 s   si bemol, sol mineur, do      la tension monte vers fa
    12 s     fa majeur                     la revelation
    16-32 s  fa, do, re mineur, si bemol   la methode, avec la batterie
    32-38 s  la batterie se retire         le catalogue, six notes pour six tuiles
    38-46 s  re mineur, tempo dedouble     le cadre et le financement
    46-54 s  retour en fa, accord final    l'appel

⚠️ Ce script ne s'ecoute pas lui-meme. Les controles en fin de fichier
portent sur ce qui se mesure — cretes, niveau, silence, synchronisation —
pas sur ce qui s'entend. Une ecoute humaine reste necessaire.
"""

from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

FE = 48000
ICI = Path(__file__).resolve().parent
REPERES = json.loads((ICI / "reperes.json").read_text())
DUREE = float(REPERES["duree"])
N = int(DUREE * FE)
TEMPS = 60.0 / REPERES["cadence"]          # 0,5 s
alea = np.random.default_rng(34)           # graine fixe : deux rendus identiques

DEMI_TONS = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}


def hz(nom: str) -> float:
    """« A4 » -> 440."""
    return 440.0 * 2 ** ((DEMI_TONS[nom[:-1]] - 9) / 12 + (int(nom[-1]) - 4))


def instants(d: float) -> np.ndarray:
    return np.arange(int(d * FE)) / FE


def passe(x, sorte, f, ordre=2):
    return sosfilt(butter(ordre, f, btype=sorte, fs=FE, output="sos"), x, axis=0)


def piste() -> np.ndarray:
    return np.zeros((N, 2))


def poser(ou: np.ndarray, x: np.ndarray, t: float, gain: float = 1.0, pan: float = 0.0) -> None:
    """Ajoute `x` a l'instant `t`. `pan` de -1 (gauche) a 1 (droite), a puissance constante."""
    i = int(round(t * FE))
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), N - i)
    if n <= 0:
        return
    if x.ndim == 1:
        angle = (pan + 1) * np.pi / 4
        ou[i : i + n, 0] += x[:n] * np.cos(angle) * gain * 1.414
        ou[i : i + n, 1] += x[:n] * np.sin(angle) * gain * 1.414
    else:
        ou[i : i + n] += x[:n] * gain


# ---------------------------------------------------------------- instruments


def nappe(f: float, d: float) -> np.ndarray:
    """Cinq voix desaccordees, adoucies : le fond harmonique."""
    t = instants(d + 1.8)
    sortie = np.zeros((len(t), 2))
    for cents, pan in ((-9, -0.8), (7, 0.8), (0, 0.0), (-4, 0.4), (5, -0.4)):
        ff = f * 2 ** (cents / 1200)
        voix = np.zeros_like(t)
        k = 1
        while k * ff < 3600 and k <= 20:
            voix += np.sin(2 * np.pi * k * ff * t + alea.uniform(0, 6.28)) / k**1.15
            k += 1
        angle = (pan + 1) * np.pi / 4
        sortie[:, 0] += voix * np.cos(angle)
        sortie[:, 1] += voix * np.sin(angle)
    montee = np.minimum(1, t / 0.75) ** 2
    chute = np.where(t < d, 1.0, np.exp(-np.maximum(t - d, 0) / 0.55))
    return sortie * (montee * chute)[:, None] * 0.085


def pince(f: float, d: float = 0.9, eclat: float = 1.0) -> np.ndarray:
    """Une note pincee, entre le marimba et la corde : l'arpege."""
    t = instants(d)
    x = np.zeros_like(t)
    for k in range(1, 7):
        x += np.sin(2 * np.pi * k * f * t) * np.exp(-t * (4.5 + 3.4 * k)) / k**1.1 * (1 if k == 1 else eclat)
    return x * (1 - np.exp(-t / 0.002))


def clavier(f: float, d: float = 1.7, force: float = 1.0) -> np.ndarray:
    """Un piano feutre : la melodie."""
    t = instants(d)
    x = np.zeros_like(t)
    for k in range(1, 9):
        fk = k * f * np.sqrt(1 + 0.0005 * k * k)        # legere inharmonicite, comme une vraie corde
        if fk > 9000:
            break
        x += np.sin(2 * np.pi * fk * t + 0.3 * k) * np.exp(-t * (1.7 + 0.95 * k)) / k**1.45
    x *= 1 - np.exp(-t / 0.006)
    return passe(x, "low", 5200) * force


def basse(f: float, d: float) -> np.ndarray:
    t = instants(d + 0.1)
    x = np.sin(2 * np.pi * f * t) + 0.42 * np.sin(4 * np.pi * f * t) + 0.16 * np.sin(6 * np.pi * f * t)
    enveloppe = np.minimum(1, t / 0.006) * np.where(t < d, 0.72 + 0.28 * np.exp(-t / 0.1), 0.72 * np.exp(-np.maximum(t - d, 0) / 0.03))
    return np.tanh(1.5 * x * enveloppe) / 1.25


def grosse_caisse(force: float = 1.0) -> np.ndarray:
    t = instants(0.42)
    f = 44 + 118 * np.exp(-t / 0.028)
    corps = np.sin(2 * np.pi * np.cumsum(f) / FE) * np.exp(-t / 0.15)
    clic = passe(alea.normal(0, 1, len(t)) * np.exp(-t / 0.003), "high", 1500) * 0.22
    return np.tanh(2.2 * (corps + clic)) * 0.8 * force


def claquement(force: float = 1.0) -> np.ndarray:
    t = instants(0.32)
    enveloppe = np.zeros_like(t)
    for dt in (0.0, 0.009, 0.019, 0.03):
        enveloppe += np.where(t >= dt, np.exp(-np.maximum(t - dt, 0) / 0.006), 0) * 0.7
    enveloppe += np.where(t >= 0.03, np.exp(-np.maximum(t - 0.03, 0) / 0.075), 0)
    return passe(alea.normal(0, 1, len(t)) * enveloppe, "band", [1100, 5200]) * 0.34 * force


def charleston(force: float = 1.0, ouvert: bool = False) -> np.ndarray:
    t = instants(0.22 if ouvert else 0.07)
    x = passe(alea.normal(0, 1, len(t)), "high", 7200) * np.exp(-t / (0.07 if ouvert else 0.016))
    return x * 0.3 * force


def grelot(force: float = 1.0) -> np.ndarray:
    t = instants(0.09)
    x = passe(alea.normal(0, 1, len(t)), "band", [4600, 9000]) * np.minimum(1, t / 0.012) * np.exp(-t / 0.028)
    return x * 0.22 * force


def cloche(f: float, d: float = 1.5, indice: float = 2.2, rapport: float = 3.5) -> np.ndarray:
    """Modulation de frequence : un timbre de cloche claire, pour les confirmations."""
    t = instants(d)
    module = np.sin(2 * np.pi * f * rapport * t) * indice * np.exp(-t / 0.22)
    return np.sin(2 * np.pi * f * t + module) * np.exp(-t / (d / 4.6)) * (1 - np.exp(-t / 0.002))


def bulle(f: float, clair: bool = False) -> np.ndarray:
    """Une petite note qui « tombe » sur sa hauteur : les apparitions."""
    t = instants(0.55)
    phase = 2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t / 0.012))) / FE
    x = np.sin(phase) * np.exp(-t / 0.12) + 0.4 * np.sin(2 * phase) * np.exp(-t / 0.05)
    if clair:
        x += 0.22 * np.sin(3 * phase) * np.exp(-t / 0.04)
    return x * (1 - np.exp(-t / 0.0015))


# ------------------------------------------------------------------ bruitages

BANDES = np.geomspace(170, 9500, 11)


def balayage(d: float, centre: np.ndarray, enveloppe: np.ndarray, largeur: float = 0.6) -> np.ndarray:
    """Un bruit dont la couleur se deplace : la matiere des souffles et des montees.

    Le filtre mobile est obtenu en melangeant onze bandes fixes, chacune
    ponderee par sa distance au centre du moment.
    """
    bruit = alea.normal(0, 1, int(d * FE))
    x = np.zeros_like(bruit)
    for fc in BANDES:
        x += passe(bruit, "band", [fc / 1.36, fc * 1.36]) * np.exp(-0.5 * (np.log2(centre / fc) / largeur) ** 2)
    return x * enveloppe


def souffle(d: float = 0.56, doux: bool = False) -> np.ndarray:
    u = instants(d) / d
    haut = 3600 if doux else 5200
    centre = np.where(u < 0.55, 320 * (haut / 320) ** (u / 0.55), haut * (800 / haut) ** ((u - 0.55) / 0.45))
    x = balayage(d, centre, np.sin(np.pi * u) ** 1.7)
    sens = 1 if alea.random() < 0.5 else -1
    angle = (sens * (u * 1.5 - 0.75) + 1) * np.pi / 4          # passe d'une oreille a l'autre
    return np.stack([x * np.cos(angle), x * np.sin(angle)], 1) * (0.5 if doux else 0.85)


def montee(d: float = 1.0, doux: bool = False) -> np.ndarray:
    u = instants(d) / d
    x = balayage(d, 380 * (9000 / 380) ** u, u**2.3, largeur=0.5)
    ton = np.sin(2 * np.pi * np.cumsum(180 * (1400 / 180) ** u) / FE) * u**2.6 * 0.16
    battement = 1 - 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(4 + 14 * u) / FE)) * u
    x = (x + ton) * battement
    x[-int(0.02 * FE) :] *= np.linspace(1, 0, int(0.02 * FE))    # un souffle de silence avant l'impact
    return np.stack([x, np.roll(x, 37)], 1) * (0.55 if doux else 0.9)


def impact(doux: bool = False, fort: bool = False) -> np.ndarray:
    d = 2.2 if fort else 1.5
    t = instants(d)
    grave = np.sin(2 * np.pi * np.cumsum(36 + 30 * np.exp(-t / 0.07)) / FE) * np.exp(-t / (0.42 if fort else 0.3))
    choc = passe(alea.normal(0, 1, len(t)) * np.exp(-t / 0.05), "low", 210, 4) * 1.6
    corps = np.sin(2 * np.pi * 148 * t) * np.exp(-t / 0.05) * 0.5
    air = passe(alea.normal(0, 1, len(t)) * np.exp(-t / (0.5 if fort else 0.3)), "band", [500, 3200]) * 0.1
    x = np.tanh(1.5 * (grave + choc + corps)) + air
    return x * (0.5 if doux else 1.0) * (1.15 if fort else 1.0)


def coup(rang: int) -> np.ndarray:
    t = instants(0.5)
    f = 62 + 46 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / FE) * np.exp(-t / 0.13)
    x += passe(alea.normal(0, 1, len(t)) * np.exp(-t / 0.012), "band", [700, 3800]) * 0.4
    return np.tanh(1.8 * x) * (0.62 + 0.14 * rang)


def scintille() -> np.ndarray:
    d = 2.6
    sortie = np.zeros((int(d * FE), 2))
    for note in ("F6", "A6", "C7", "F7", "G7", "A7", "C8", "G6"):
        for _ in range(2):
            depart = alea.uniform(0, 0.45)
            x = cloche(hz(note) * alea.choice([1, 1, 2]) * 0.5, 1.7, indice=0.7, rapport=2.0) * alea.uniform(0.3, 1)
            i = int(depart * FE)
            angle = (alea.uniform(-0.9, 0.9) + 1) * np.pi / 4
            sortie[i : i + len(x), 0] += x[: len(sortie) - i] * np.cos(angle)
            sortie[i : i + len(x), 1] += x[: len(sortie) - i] * np.sin(angle)
    return sortie * 0.09


def touche() -> np.ndarray:
    t = instants(0.03)
    f = alea.uniform(2300, 3400)
    x = passe(alea.normal(0, 1, len(t)), "band", [f, f * 1.9]) * np.exp(-t / 0.0035)
    x += np.sin(2 * np.pi * alea.uniform(1500, 1900) * t) * np.exp(-t / 0.004) * 0.5
    return x * alea.uniform(0.6, 1.0)


def tic(f: float = 2100) -> np.ndarray:
    t = instants(0.05)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008) * (1 - np.exp(-t / 0.0006))


def clic_souris() -> np.ndarray:
    d = int(0.16 * FE)
    x = np.zeros(d)
    for depart, f, g in ((0.0, 1250, 1.0), (0.07, 1750, 0.6)):
        t = instants(0.03)
        grain = passe(alea.normal(0, 1, len(t)), "high", 2800) * np.exp(-t / 0.0022) + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.004)
        i = int(depart * FE)
        x[i : i + len(t)] += grain * g
    return x


def glisse(haut: int = 0) -> np.ndarray:
    d = 0.5
    u = instants(d) / d
    f = 330 * 2 ** (haut * 2 / 12) * (2 ** (u * 0.75))
    x = np.sin(2 * np.pi * np.cumsum(f) / FE) * np.sin(np.pi * u) ** 1.4
    return passe(x, "low", 1800)


def creux() -> np.ndarray:
    t = instants(0.5)
    f = 233 - 40 * (1 - np.exp(-t / 0.12))
    return np.sin(2 * np.pi * np.cumsum(f) / FE) * np.exp(-t / 0.16) * (1 - np.exp(-t / 0.004))


def bip_camera() -> np.ndarray:
    x = np.zeros(int(0.3 * FE))
    for depart in (0.0, 0.14):
        t = instants(0.075)
        i = int(depart * FE)
        x[i : i + len(t)] += np.sin(2 * np.pi * 1320 * t) * np.minimum(1, t / 0.004) * np.minimum(1, (0.075 - t) / 0.008)
    return x


def sonar() -> np.ndarray:
    d = 2.0
    x = np.zeros(int(d * FE))
    for k, depart in enumerate((0.0, 0.38, 0.76)):
        son = cloche(hz("A5"), 1.1, indice=0.5, rapport=2.0) * 0.55**k
        i = int(depart * FE)
        x[i : i + len(son)] += son[: len(x) - i]
    return x


def trait(rang: int) -> np.ndarray:
    d = 0.24
    u = instants(d) / d
    air = balayage(d, 1300 * (5600 / 1300) ** u, np.sin(np.pi * u) ** 1.5, largeur=0.5) * 0.6
    note = pince(hz(("F4", "A4", "C5")[rang]), d, 0.8) * 0.9
    return air + note


# ------------------------------------------------------------- espace et echo


def salle(d: float = 2.6, rt: float = 2.0) -> np.ndarray:
    """La reponse d'une salle : du bruit qui s'eteint, les aigus plus vite que les graves."""
    t = instants(d)
    reponse = np.zeros((len(t), 2))
    for c in range(2):
        bruit = alea.normal(0, 1, len(t))
        reponse[:, c] = passe(bruit, "low", 1700) * np.exp(-t * 6.91 / rt) + 0.85 * passe(bruit, "high", 1700) * np.exp(-t * 6.91 / (rt * 0.42))
    reponse = np.vstack([np.zeros((int(0.02 * FE), 2)), reponse])      # 20 ms avant les premiers echos
    return reponse / np.sqrt((reponse**2).sum(0)).max()


SALLE = salle()


def reverberer(x: np.ndarray, mouille: float) -> np.ndarray:
    echo = np.stack([fftconvolve(x[:, c], SALLE[:, c])[: len(x)] for c in range(2)], 1)
    return x + mouille * passe(echo, "high", 180)


def echo_alterne(x: np.ndarray, retard: float = 0.375, retour: float = 0.42, tours: int = 6) -> np.ndarray:
    """Un echo qui passe d'une oreille a l'autre, a la croche pointee."""
    sortie = x.copy()
    source = x.mean(1)
    pas = int(retard * FE)
    for k in range(1, tours + 1):
        source = passe(source, "low", 3200) * retour
        sortie[k * pas :, k % 2] += source[: len(x) - k * pas] * 1.3
    return sortie


def pompe(battues: list[float], creux_: float = 0.45, retour: float = 0.17) -> np.ndarray:
    """La nappe et la basse s'effacent sous chaque coup de grosse caisse."""
    gain = np.ones(N)
    for tk in battues:
        i = int(tk * FE)
        n = min(N - i, int(0.7 * FE))
        gain[i : i + n] = np.minimum(gain[i : i + n], 1 - creux_ * np.exp(-np.arange(n) / FE / retour))
    return gain[:, None]


# ------------------------------------------------------------------- partition

ACCORDS = {
    "Dm9": ("D2", ["D3", "A3", "C4", "E4", "F4"]),
    "Bb": ("Bb1", ["Bb2", "F3", "A3", "D4", "F4"]),
    "Gm7": ("G2", ["G3", "Bb3", "D4", "F4"]),
    "Gm9": ("G2", ["G3", "Bb3", "D4", "F4", "A4"]),
    "Csus": ("C2", ["C3", "G3", "Bb3", "D4", "F4"]),
    "C": ("C2", ["C3", "G3", "C4", "E4"]),
    "F9": ("F2", ["F3", "A3", "C4", "G4"]),
    "F": ("F2", ["F3", "A3", "C4", "F4"]),
    "C/E": ("E2", ["E3", "G3", "C4", "E4"]),
    "Dm7": ("D2", ["D3", "F3", "A3", "C4", "F4"]),
    "Am7": ("A2", ["A3", "C4", "E4", "G4"]),
}
GRILLE = [
    (0, 6, "Dm9"), (6, 8, "Bb"), (8, 10, "Gm7"), (10, 12, "Csus"), (12, 14, "F9"), (14, 16, "C/E"),
    (16, 18, "F"), (18, 20, "C/E"), (20, 22, "Dm7"), (22, 24, "Bb"),
    (24, 26, "F"), (26, 28, "C/E"), (28, 30, "Dm7"), (30, 31, "Bb"), (31, 32, "C"),
    (32, 34, "Bb"), (34, 36, "Am7"), (36, 37, "Gm7"), (37, 38, "Csus"),
    (38, 40, "Dm9"), (40, 42, "Bb"), (42, 44, "Gm9"), (44, 45, "Csus"), (45, 46, "C"),
    (46, 48, "F"), (48, 50, "C/E"), (50, 51, "Dm7"), (51, 52, "Bb"), (52, 54, "F9"),
]  # fmt: skip
MOTIFS = {  # (temps dans la mesure, note)
    "F": [(0, "A4"), (1.5, "C5"), (2.5, "F5")],
    "C/E": [(0, "G4"), (1.5, "C5"), (2.5, "E5"), (3.5, "D5")],
    "Dm7": [(0, "F4"), (1.5, "A4"), (2.5, "D5")],
    "Bb": [(0, "D5"), (1.5, "F5"), (2.5, "A5"), (3.5, "G5")],
    "C": [(0, "E5"), (1, "G5")],
}
CALMES = {"Dm9": [(0, "E5"), (2, "D5")], "Bb": [(0, "F5"), (2, "D5")], "Gm9": [(0, "A4"), (2, "Bb4")], "Csus": [(0, "G4")], "C": [(0, "E5")]}
GAMME_BULLES = ["F5", "A5", "C6", "D6", "E6", "G6"]      # six tuiles, six notes qui montent


def octave(nom: str, de: int = 1) -> str:
    return nom[:-1] + str(int(nom[-1]) + de)


def plein(t: float) -> bool:
    """Les passages ou la batterie joue en entier."""
    return 16 <= t < 32 or 46 <= t < 50


def composer() -> np.ndarray:
    nap, bas, arp, mel, bat = piste(), piste(), piste(), piste(), piste()
    battues: list[float] = []

    for debut, fin, nom in GRILLE:
        fondamentale, voix = ACCORDS[nom]
        duree = fin - debut
        temps_de_mesure = int(round(duree / TEMPS))

        for note in voix:
            poser(nap, nappe(hz(note), duree), debut)
        if nom == "F9" and debut >= 52:                           # l'accord final, plus large
            for note in ("F4", "C5", "A5"):
                poser(nap, nappe(hz(note), duree), debut, 0.6)

        # --- basse ---
        if debut < 6:
            pass                                                   # l'ouverture reste en suspens
        elif debut < 12:
            for k in range(temps_de_mesure * 2):                   # croches qui montent en puissance
                tk = debut + k * TEMPS / 2
                poser(bas, basse(hz(octave(fondamentale)), TEMPS * 0.42), tk, 0.34 + 0.46 * (tk - 6) / 6)
        elif plein(debut):
            for temps_, long_, hauteur, force in ((0, 0.9, 0, 1.0), (1.5, 0.4, 0, 0.7), (2, 0.9, 0, 0.95), (3, 0.4, 1, 0.6), (3.5, 0.4, 0, 0.7)):
                if temps_ < temps_de_mesure:
                    poser(bas, basse(hz(octave(fondamentale, hauteur)), long_ * TEMPS), debut + temps_ * TEMPS, 0.8 * force)
        elif 36 <= debut < 38:
            for k in range(temps_de_mesure * 2):
                poser(bas, basse(hz(fondamentale), TEMPS * 0.4), debut + k * TEMPS / 2, 0.6)
        else:                                                      # notes tenues
            poser(bas, basse(hz(fondamentale), duree * 0.96), debut, 0.72 if debut >= 12 else 0.5)

        # --- arpege ---
        aigus = [octave(n) for n in voix]
        if 2 <= fin and debut < 6:                                 # un battement sourd sous la question
            for k in range(int((6 - 2) / (TEMPS / 2))):
                tk = 2 + k * TEMPS / 2
                poser(arp, pince(hz("D3") * (2 if k % 4 == 3 else 1), 0.5, 0.45), tk, 0.16 + 0.3 * k / 16, 0.3 * (-1) ** k)
        elif debut >= 6:
            ordre = [0, 2, 1, 3, 2, 3, 1, 2]
            niveau = 0.34 if debut < 12 else 0.5 if debut < 16 else 0.62 if plein(debut) else 0.46 if debut < 46 else 0.5
            if 50 <= debut:
                niveau = 0.3
            for k in range(temps_de_mesure * 2):
                note = aigus[ordre[k % 8] % len(aigus)]
                accent = 1.0 if k % 4 == 0 else 0.72
                poser(arp, pince(hz(note), 0.8, 1.3), debut + k * TEMPS / 2, niveau * accent, 0.55 * (-1) ** k)

        # --- melodie ---
        if plein(debut):
            for temps_, note in MOTIFS.get(nom, []):
                if temps_ < temps_de_mesure:
                    haut = 1 if 24 <= debut < 32 and temps_ >= 2.5 else 0   # deuxieme passage : la fin du motif a l'octave
                    poser(mel, clavier(hz(octave(note, haut))), debut + temps_ * TEMPS, 0.52, -0.15)
        elif 38 <= debut < 46:
            for temps_, note in CALMES.get(nom, []):
                poser(mel, clavier(hz(note), 2.4), debut + temps_ * TEMPS, 0.5, 0.15)

    # La revelation : une gamme qui s'ouvre, puis l'accord pose.
    for k, note in enumerate(("F4", "A4", "C5", "F5", "G5", "A5", "C6")):
        poser(mel, clavier(hz(note), 2.2), 12.0 + k * 0.125, 0.4 + 0.035 * k, -0.5 + k * 0.16)
    for note in ("F3", "C4", "A4", "G5"):
        poser(mel, clavier(hz(note), 2.6), 13.0, 0.3)
    for k, note in enumerate(("E4", "G4", "C5", "E5", "G5", "C6")):
        poser(mel, clavier(hz(note), 1.8), 14.0 + k * 0.25, 0.4, 0.4 - k * 0.14)
    # Les deux titres de l'ouverture. Leurs instants sont lus dans les reperes :
    # ecrits en dur, ils sont restes a 3 s et 4,5 s le jour ou l'image a avance
    # les titres d'une seconde — la musique saluait alors une phrase deja la.
    titres = [r["t"] for r in REPERES["reperes"] if r["type"] == "impact" and r["t"] < 6][:2]
    assert len(titres) == 2, "l'ouverture doit compter deux titres"
    for note in ("A4", "D5"):
        poser(mel, clavier(hz(note), 2.6), titres[0], 0.42)
    for note in ("F4", "A4", "E5"):
        poser(mel, clavier(hz(note), 2.6), titres[1], 0.42)
    # La fin : deux notes sur le logo, puis l'accord qui reste.
    poser(mel, clavier(hz("F5"), 2.4), 50.0, 0.5)
    poser(mel, clavier(hz("D5"), 2.4), 51.0, 0.48)
    for k, note in enumerate(("F3", "C4", "A4", "C5", "G5", "F6")):
        poser(mel, clavier(hz(note), 3.2), 52.0 + k * 0.03, 0.3, -0.4 + k * 0.16)

    # --- batterie ---
    for mesure in range(int(DUREE // 2)):
        t0 = 2.0 * mesure
        if plein(t0):
            for temps_, force in ((0, 1.0), (2, 0.95)) + (((3.5, 0.55),) if mesure % 2 else ()):
                poser(bat, grosse_caisse(force), t0 + temps_ * TEMPS)
                battues.append(t0 + temps_ * TEMPS)
            for temps_ in (1, 3):
                poser(bat, claquement(), t0 + temps_ * TEMPS, 1.0, 0.08)
            for k in range(8):
                poser(bat, charleston(1.0 if k % 2 else 0.4, ouvert=(k == 7 and mesure % 4 == 3)), t0 + k * TEMPS / 2, 1.0, 0.25)
            for k in range(16):
                poser(bat, grelot(1.0 if k % 4 == 2 else 0.55), t0 + k * TEMPS / 4, 1.0, -0.35)
        elif 32 <= t0 < 36:                                        # le catalogue : la grosse caisse se retire
            for temps_ in (1, 3):
                poser(bat, claquement(0.7), t0 + temps_ * TEMPS, 1.0, 0.08)
            for k in range(8):
                poser(bat, charleston(0.8 if k % 2 else 0.3), t0 + k * TEMPS / 2, 1.0, 0.25)
        elif 36 <= t0 < 38:                                        # et revient, pour relancer
            for k in range(4):
                poser(bat, grosse_caisse(0.8), t0 + k * TEMPS)
                battues.append(t0 + k * TEMPS)
            for k in range(12):                                    # roulement : croches, puis doubles
                tk = 37.0 + (k * 0.125 if k < 4 else 0.5 + (k - 4) * 0.0625)
                poser(bat, claquement(0.28 + 0.05 * k), tk)
        elif 38 <= t0 < 46:                                        # tempo dedouble
            poser(bat, grosse_caisse(0.9), t0)
            battues.append(t0)
            poser(bat, claquement(0.55), t0 + 2 * TEMPS, 1.0, 0.08)
            if t0 >= 42:
                for k in range(8):
                    poser(bat, charleston(0.7 if k % 2 else 0.25), t0 + k * TEMPS / 2, 1.0, 0.25)
        elif 12 <= t0 < 16:
            if t0 == 14:
                poser(bat, grosse_caisse(0.7), t0)
                battues.append(t0)
                for tk in (15.5, 15.75):                           # deux claquements d'appel
                    poser(bat, claquement(0.6), tk)
        elif 50 <= t0 < 52:
            for tk in (50.0, 51.0):
                poser(bat, grosse_caisse(0.75), tk)
                battues.append(tk)
        elif 8 <= t0 < 12:                                         # un tic-tac discret sous les trois refus
            for k in range(16):
                poser(bat, charleston(0.35 + 0.3 * (t0 - 8 + k / 8) / 4), t0 + k * TEMPS / 4, 1.0, 0.3 * (-1) ** k)

    # --- niveaux par passage, espace, puis mise en commun ---
    t = np.arange(N) / FE
    courbe_nappe = np.interp(t, [0, 3, 6, 11.9, 12, 16, 32, 38, 46, 52, 54], [0, 0.75, 0.85, 1.0, 1.15, 0.85, 0.85, 1.0, 0.9, 1.1, 1.0])
    nap = passe(nap * courbe_nappe[:, None], "low", 3000)
    creux_ = pompe(battues)
    nap = reverberer(nap, 0.3) * creux_
    bas = passe(bas, "low", 420, 4) * (0.6 + 0.4 * creux_)
    arp = reverberer(echo_alterne(arp), 0.32) * (0.75 + 0.25 * creux_)
    mel = reverberer(echo_alterne(mel, 0.375, 0.26, 3), 0.45)
    bat = reverberer(bat, 0.07)
    pupitres = {"nappe": nap * 0.36, "basse": bas * 0.4, "arpege": arp * 0.74, "melodie": mel * 0.5, "batterie": bat * 0.95}
    for nom, x in pupitres.items():                                # ce que pese chaque pupitre dans le total
        print(f"  {nom:9} {db(x):6.1f} dB · crete {20 * np.log10(np.abs(x).max()):6.1f} dBFS")
    return sum(pupitres.values())


def bruiter() -> np.ndarray:
    sec, mouille = piste(), piste()
    for r in REPERES["reperes"]:
        t, sorte = r["t"], r["type"]
        if sorte == "touche":
            poser(sec, touche(), t, 0.11, alea.uniform(-0.25, 0.25))
        elif sorte == "roule":
            poser(sec, souffle(0.3, doux=True), t - 0.05, 0.5)
            poser(sec, tic(1500), t + 0.2, 0.12)
        elif sorte == "souffle":
            x = souffle(0.5 if r.get("doux") else 0.62, doux=bool(r.get("doux")))
            poser(mouille, x, t, 0.34)
        elif sorte == "impact":
            poser(mouille, impact(doux=bool(r.get("doux")), fort=bool(r.get("fort"))), t, 0.62)
        elif sorte == "coup":
            poser(mouille, coup(r["rang"]), t, 0.7)
        elif sorte == "montee":
            poser(mouille, montee(r["d"], doux=bool(r.get("doux"))), t, 0.3)
        elif sorte == "scintille":
            poser(mouille, scintille(), t, 1.0)
        elif sorte == "pop":
            note = GAMME_BULLES[r.get("note", 0) % len(GAMME_BULLES)]
            poser(mouille, bulle(hz(note), bool(r.get("clair"))), t, 0.26 if r.get("clair") else 0.2, (r.get("note", 0) - 2.5) * 0.16)
        elif sorte == "pas":
            poser(mouille, bulle(hz(("F4", "G4", "A4", "C5")[r["rang"]])), t, 0.26)
        elif sorte == "tic":
            poser(sec, tic(), t, 0.1, 0.2)
        elif sorte == "coche":
            decalage = r.get("note", 0)
            for k, note in enumerate((("C6", "F6"), ("D6", "G6"), ("F6", "A6"))[decalage % 3]):
                poser(mouille, bulle(hz(note)), t + k * 0.055, 0.15, 0.3)
        elif sorte == "carillon":
            notes = ("A5", "C6") if r.get("petit") else ("A5", "C6", "F6")
            for k, note in enumerate(notes):
                poser(mouille, cloche(hz(note), 1.6), t + k * 0.07, 0.12 if r.get("petit") else 0.16, -0.3 + 0.3 * k)
        elif sorte == "clic":
            poser(sec, clic_souris(), t, 0.3)
        elif sorte == "glisse":
            poser(mouille, glisse(r.get("haut", 0)), t, 0.1, -0.2 + 0.2 * r.get("haut", 0))
        elif sorte == "creux":
            poser(mouille, creux(), t, 0.3, 0.45)
        elif sorte == "rec":
            poser(sec, bip_camera(), t, 0.09, -0.3)
        elif sorte == "sonar":
            poser(mouille, sonar(), t, 0.12, 0.3)
        elif sorte == "trait":
            poser(mouille, trait(r["rang"]), t, 0.28, -0.5 + 0.5 * r["rang"])
        else:
            raise ValueError(f"repere sonore inconnu : {sorte}")
    return sec + reverberer(mouille, 0.22)


def limiter(x: np.ndarray, plafond: float = 0.74) -> np.ndarray:
    """Baisse le volume juste avant chaque crete, au lieu de l'ecreter.

    Les deux premiers essais arrondissaient la forme d'onde. Le resultat
    tenait en apparence (-2,5 dBFS sur les echantillons) et depassait en
    realite : +0,7 dB en crete vraie, entre deux echantillons — de quoi
    saturer a la conversion. Ici la crete est mesuree sur le signal
    surechantillonne quatre fois, et le gain descend 3 ms a l'avance.

    Le plafond est a -2,6 dB et non a -1 : la compression AAC du fichier
    final ajoute environ 1 dB de crete (mesure : -1,4 dB dans le WAV,
    -0,4 dB dans le MP4). C'est le MP4 qui doit tenir sous -1 dB.
    """
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    from scipy.signal import resample_poly

    vraie = np.abs(resample_poly(x, 4, 1, axis=0)).max(1).reshape(-1, 4).max(1)
    avance = int(0.003 * FE)
    crete = maximum_filter1d(vraie, size=2 * avance + 1)
    reduction = 1 - np.minimum(1, plafond / np.maximum(crete, 1e-9))
    # Retour progressif (80 ms) : sans lui, le gain remonte d'un coup et on entend le pompage.
    pas = 16
    grossier = reduction[: len(reduction) // pas * pas].reshape(-1, pas).max(1)
    retour = np.exp(-pas / FE / 0.08)
    for k in range(1, len(grossier)):
        grossier[k] = max(grossier[k], grossier[k - 1] * retour)
    lisse = np.maximum(reduction, np.interp(np.arange(len(x)), np.arange(len(grossier)) * pas + pas / 2, grossier))
    gain = 1 - uniform_filter1d(maximum_filter1d(lisse, size=avance), size=avance)
    limiter.bilan = (20 * np.log10(gain.min()), float((gain < 0.995).mean()))
    return x * gain[:, None]


def raboter(x: np.ndarray, genou: float = 0.62, plafond: float = 0.98) -> np.ndarray:
    """Arrondit la pointe des attaques (grosse caisse, impacts), quelques millisecondes.

    Seul, ce rabot laisse passer des cretes vraies ; il ne sert qu'a soulager
    le limiteur, qui sans lui baissait le volume de 6 dB un tiers du temps.
    """
    a = np.abs(x)
    return np.sign(x) * np.where(a <= genou, a, genou + (plafond - genou) * np.tanh((a - genou) / (plafond - genou)))


def sonie(x: np.ndarray) -> float:
    """Niveau integre, en LUFS, mesure par ffmpeg (EBU R 128)."""
    import re
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        ecrire(Path(f.name), x)
        journal = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f.name, "-af", "ebur128", "-f", "null", "-"],
                                 capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", journal)[-1])


def ecrire(chemin: Path, x: np.ndarray) -> None:
    with wave.open(str(chemin), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(FE)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def db(x: np.ndarray) -> float:
    return 20 * np.log10(max(np.sqrt((x**2).mean()), 1e-9))


if __name__ == "__main__":
    musique, bruitages = composer(), bruiter()
    mixage = passe(musique * 1.0 + bruitages * 1.5, "high", 28)
    # Inclinaison d'ensemble : un peu moins de sous-grave, un peu plus de
    # presence. Mesure avant : sous-grave -19, medium -22, aigu -32 — sombre,
    # et presque vide sur un telephone, qui ne rend pas le sous-grave.
    mixage = mixage - 0.22 * passe(mixage, "low", 110) + 0.7 * passe(mixage, "high", 2400)
    t = np.arange(N) / FE
    mixage *= np.interp(t, [0, 0.02, DUREE - 0.75, DUREE - 0.03, DUREE], [0, 1, 1, 0, 0])[:, None]   # le fondu final suit le fondu au noir
    # Cible : -15 LUFS. Les plateformes ramenent les videos vers -14 ; a -14
    # tout juste, avec un plafond de crete a -2,6 dB, le limiteur travaillait
    # 45 % du temps (jusqu'a -4,8 dB) — assez pour faire respirer la musique
    # a chaque coup de grosse caisse. Un decibel de moins lui rend sa marge.
    mixage *= 0.5 / np.percentile(np.abs(mixage), 99.9)
    for _ in range(4):
        essai = limiter(raboter(mixage))
        ecart = -15.0 - sonie(essai)
        if abs(ecart) < 0.15:
            break
        mixage *= 10 ** (ecart / 20)
    mixage = limiter(raboter(mixage))
    sortie = ICI / "sortie"
    sortie.mkdir(exist_ok=True)
    ecrire(sortie / "son.wav", mixage)

    # ---- ce qui se mesure ----
    assert np.isfinite(mixage).all(), "le mixage contient des valeurs non finies"
    print(f"duree {len(mixage) / FE:.2f} s · crete {20 * np.log10(np.abs(mixage).max()):.1f} dBFS · niveau moyen {db(mixage):.1f} dB")
    print(f"musique seule {db(musique):.1f} dB · bruitages seuls {db(bruitages):.1f} dB (avant limiteur)")
    for debut, fin, nom in ((0, 6, "recherche"), (6, 12, "probleme"), (12, 16, "revelation"), (16, 32, "methode"), (32, 38, "catalogue"), (38, 46, "cadre"), (46, 54, "appel")):
        print(f"  {nom:11} {db(mixage[int(debut * FE) : int(fin * FE)]):6.1f} dB")
    silence = np.abs(mixage).max(1) < 1e-4
    blancs = np.diff(np.concatenate([[0], silence.astype(int), [0]]))
    longs = [(a / FE, (b - a) / FE) for a, b in zip(np.where(blancs == 1)[0], np.where(blancs == -1)[0]) if (b - a) > 0.25 * FE and a / FE < DUREE - 1]
    print(f"limiteur : {limiter.bilan[0]:.1f} dB au plus fort, actif {limiter.bilan[1]:.0%} du temps")
    print("silences de plus de 0,25 s :", longs or "aucun")
    bandes = ((28, 120, "sous-grave"), (120, 500, "grave"), (500, 2000, "medium"), (2000, 6000, "aigu"), (6000, 16000, "brillance"))
    print("equilibre :", " · ".join(f"{nom} {db(passe(mixage, 'band', [a, b], 4)):.0f}" for a, b, nom in bandes))
    milieu, cote = mixage.sum(1) / 2, (mixage[:, 0] - mixage[:, 1]) / 2
    print(f"mono {db(milieu):.1f} dB · largeur {db(cote):.1f} dB · sonie {sonie(mixage):.1f} LUFS")
