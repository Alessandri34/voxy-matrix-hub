#!/usr/bin/env python3
"""Relit tout le texte du film — a l'ecran et a la voix — avant de le monter.

Un film publicitaire d'organisme de formation est tenu par les memes regles
que les scripts : pas de « gratuit », pas de « finance a 100 % », pas de
resultat promis, pas de prix, pas de « formation obligatoire ». Les listes
reprennent celles de `../controle-scripts.py`, qui ne s'importe pas (il lit
un fichier des son chargement).

S'y ajoutent deux controles propres a l'image :
- **pas de logo Qualiopi**. La marque est interdite « dans une publicite pour
  une action de formation en particulier » (CLAUDE.md §8sexies). La mention
  ecrite, elle, est permise, a condition de porter la categorie d'action ;
- **pas de montant en euros** : aucun prix n'est publie (decision D9).

Et, pour la voix off (`voix.json`), ce qu'une oreille ne rattrape pas :
- le **debit**, compte en SYLLABES : « Reservez votre diagnostic » fait trois
  mots et huit syllabes, et c'est la syllabe qui prend du temps ;
- les **silences** : la voix se tait sur l'impact de 12 s et sur la fin ;
- les **deux boucles decalees** de `../A5_Structure_Retention.md` (L1 a L3) ;
- l'accord entre `voix.json` et `VOIX_OFF.md` : une replique corrigee dans
  l'un et pas dans l'autre finit enregistree dans sa mauvaise version.

    python3 controler-texte.py                 code de sortie 1 s'il y a une erreur
    python3 controler-texte.py --sous-titres   ecrit aussi sortie/voix.srt
    python3 controler-texte.py --detail        syllabes et temps de chaque replique
"""

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCE = ICI / "film.html"
VOIX = ICI / "voix.json"
DOCUMENT = ICI / "VOIX_OFF.md"

BANNIES = ["100 % finance", "100% finance", "sans reste a charge", "machine a cash", "paravent",
           "sans depenser un centime", "ne vous coute rien", "entierement finance", "formation offerte",
           "reste a charge nul", "gratuit", "offert", "formation obligatoire", "obligatoire"]  # fmt: skip
PROMESSES = [r"\bgaranti", r"vous (?:gagnerez|aurez|obtiendrez|doublerez)", r"\+\s*\d+\s*%", r"x\s*\d+\s+(?:vos|votre|plus)",
             r"(?:premiere|1re) place", r"(?:plus|davantage) de (?:clients|chiffre|revenus?|ventes)\b",
             r"(?:augmente|fera augmenter|fait augmenter) (?:votre|ton) (?:ca|chiffre)", r"(?:usine|machine) a ",
             r"\bdomination\b", r"\btop 1 ?%", r"\bhack\b",
             # Ce qu'une voix glisse plus facilement qu'un titre : le client qui vient.
             r"(?:fera|fait|feront|font) venir", r"clients? (?:viendront|arriveront|reviendront)",
             r"(?:attire[rz]?|remplir|remplissez) (?:des |vos |plus de |votre )"]  # fmt: skip
# La manoeuvre de retention annoncee au lieu d'etre tenue (A5 §3).
ANNONCES = [r"restez? jusqu", r"jusqu'a la fin", r"jusqu'au bout", r"ne partez pas", r"attendez la (?:fin|suite)"]


def plat(texte: str) -> str:
    return unicodedata.normalize("NFD", texte.lower().replace("’", "'")).encode("ascii", "ignore").decode()


def mots(texte: str) -> int:
    """Un mot = ce qu'une espace separe ; un signe de ponctuation isole ne se dit pas."""
    return sum(1 for m in texte.split() if re.search(r"\w", m))


MONOSYLLABES = {"le", "ce", "de", "je", "me", "ne", "que", "se", "te"}


def syllabes(texte: str) -> int:
    """Estime le nombre de syllabes DITES, a une pres par phrase.

    Regle : un groupe de voyelles = une syllabe ; le « e » final muet ne
    compte pas (« cherche », « trouve », « minutes ») ; « qu » ne porte pas de
    voyelle. L'estimation sert a refuser une replique qui ne tient pas dans
    sa fenetre, pas a scander un vers : c'est le comedien qui a le dernier mot.
    """
    total = 0
    for mot in re.findall(r"[a-z']+", plat(texte).replace("vformations", "veformations")):
        for partie in mot.split("'"):
            partie = partie.replace("qu", "k")
            groupes = len(re.findall(r"[aeiouy]+", partie))
            if partie not in MONOSYLLABES and re.search(r"[^aeiouy]es?$", partie) and groupes > 1:
                groupes -= 1
            total += groupes
    return total


def duree_dite(texte: str, debit: float) -> float:
    """Le temps qu'il faut pour dire la replique : ses syllabes, plus ses respirations."""
    interieur = texte.strip().rstrip(".?!…")
    return syllabes(texte) / debit + 0.35 * len(re.findall(r"[.?!…:]", interieur)) + 0.15 * interieur.count(",")


def fautes_de_fond(texte: str) -> list[str]:
    """Les regles qui valent pour tout mot du film, qu'il soit lu ou entendu."""
    bas = plat(texte)
    erreurs = [f"formulation bannie : « {m} »" for m in BANNIES if m in bas]
    erreurs += [f"promesse de resultat : motif « {motif} »" for motif in PROMESSES if re.search(motif, bas)]
    if "€" in texte or re.search(r"\b\d+\s*euros?\b", bas):
        erreurs.append("un montant en euros (aucun prix n'est publie : D9)")
    if "qualiopi" in bas and "au titre des actions de formation" not in bas:
        erreurs.append("Qualiopi est cite sans la categorie d'action (« au titre des actions de formation »)")
    return erreurs


# ------------------------------------------------------------------ l'ecran


def texte_a_l_ecran(source: str) -> str:
    corps = source[source.index("<body") : source.index("<script src=")]
    corps = re.sub(r"<!--.*?-->|<svg.*?</svg>", " ", corps, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps))).strip()


def controler_ecran() -> list[str]:
    source = SOURCE.read_text(encoding="utf8")
    erreurs = fautes_de_fond(texte_a_l_ecran(source))
    if re.search(r"qualiopi[\w-]*\.(?:png|svg|jpg)|mag-qualiopi", source, re.I):
        erreurs.append("le logo Qualiopi (ou une image qui le montre) est utilise dans le film")
    return erreurs


# ------------------------------------------------------------------- la voix


def plan(repere: str) -> int:
    """« P4-2 » -> 4, « P7a » -> 7."""
    return int(re.match(r"P(\d)", repere).group(1))


def controler_voix(voix: dict) -> list[str]:
    erreurs = []
    repliques = voix["repliques"]
    debit = voix["debit"]["syllabes_par_seconde"]
    dit = " ".join(r["texte"] for r in repliques)
    erreurs += fautes_de_fond(dit)
    erreurs += [f"retention annoncee au lieu d'etre tenue : motif « {m} »" for m in ANNONCES if re.search(m, plat(dit))]

    document = DOCUMENT.read_text(encoding="utf8") if DOCUMENT.exists() else None
    if document is None:
        erreurs.append("VOIX_OFF.md manque : le comedien n'a pas sa direction")
    precedente = None
    for r in repliques:
        ref, de, a = r["repere"], r["de"], r["a"]
        duree, besoin = a - de, duree_dite(r["texte"], debit)
        if besoin > duree + 0.05:
            erreurs.append(f"{ref} ne tient pas : {syllabes(r['texte'])} syllabes et leurs respirations demandent {besoin:.1f} s, la replique en a {duree:.1f}")
        f0, f1 = r["fenetre"]
        if de < f0 - 1e-9 or a > f1 + 1e-9:
            erreurs.append(f"{ref} sort de sa fenetre : {de}-{a} s pour {f0}-{f1} s")
        for s0, s1, pourquoi in voix["silences"]:
            if de < s1 and a > s0:
                erreurs.append(f"{ref} parle pendant un silence impose ({s0}-{s1} s : {pourquoi})")
        if precedente and de < precedente["a"] + 0.3:
            erreurs.append(f"{ref} suit {precedente['repere']} sans respiration ({de - precedente['a']:.2f} s)")
        for champ in ("intention", "intonation", "appuis"):
            if not r.get(champ):
                erreurs.append(f"{ref} n'a pas de « {champ} » : une replique sans direction se lit, elle ne se joue pas")
        for appui in r.get("appuis", []):
            if plat(appui) not in plat(r["texte"]):
                erreurs.append(f"{ref} appuie sur « {appui} », qui n'est pas dans la replique")
        if document is not None and r["texte"] not in document:
            erreurs.append(f"{ref} : la replique de voix.json n'est pas, mot pour mot, dans VOIX_OFF.md")
        precedente = r

    # Les variantes d'accroche et les prises de secours seront enregistrees dans la meme
    # seance : elles passent le meme controle, dans la fenetre de la replique qu'elles remplacent.
    quand = {r["repere"]: r for r in repliques}
    remplacantes = [("P1", v["texte"], f"accroche « {v['nom']} »") for v in voix.get("variantes_accroche", [])]
    remplacantes += [(v["repere"], v["texte"], f"secours {v['repere']}") for v in voix.get("prises_de_secours", [])]
    for repere, texte, nom in remplacantes:
        erreurs += [f"{nom} · {e}" for e in fautes_de_fond(texte)]
        f0, f1 = quand[repere]["fenetre"]
        besoin = duree_dite(texte, debit)
        if besoin > f1 - f0 + 0.05:
            erreurs.append(f"{nom} ne tient pas : il lui faut {besoin:.1f} s, la fenetre de {repere} en a {f1 - f0:.1f}")
        if document is not None and texte not in document:
            erreurs.append(f"{nom} : le texte de voix.json n'est pas, mot pour mot, dans VOIX_OFF.md")

    # Les boucles decalees (A5, regles L1 a L3).
    boucles = voix.get("boucles", {})
    if not {"A", "B"} <= set(boucles):
        erreurs.append("L1 : le script doit declarer au moins deux boucles, A et B")
        return erreurs
    for nom, b in boucles.items():
        for bout in ("ouvre", "ferme"):
            if b.get(bout) not in quand:
                erreurs.append(f"L3 : la boucle {nom} ne dit pas ou elle {bout} (ou ce repere n'existe pas)")
                return erreurs
        if quand[b["ferme"]]["de"] <= quand[b["ouvre"]]["de"]:
            erreurs.append(f"L3 : la boucle {nom} se ferme avant de s'ouvrir")
    a, b = boucles["A"], boucles["B"]
    if plan(a["ouvre"]) != 1:
        erreurs.append("la boucle A doit s'ouvrir a l'accroche (plan 1)")
    if plan(a["ferme"]) not in (6, 7):
        erreurs.append(f"L2 : la boucle A se referme en {a['ferme']} ; elle ne doit se refermer qu'aux plans 6 ou 7")
    if quand[b["ouvre"]]["de"] >= quand[a["ferme"]]["de"]:
        erreurs.append("B doit s'ouvrir AVANT que A se referme : c'est tout le mecanisme")
    if quand[b["ferme"]]["de"] > quand[a["ferme"]]["de"]:
        erreurs.append("B se referme apres A : il ne reste plus de question en suspens entre les deux")
    return erreurs


def ecrire_sous_titres(voix: dict, chemin: Path) -> None:
    """Un .srt des repliques : pose sur le film dans un lecteur, il sert de prompteur a la repetition."""

    def code(t: float) -> str:
        ms = round(t * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    blocs = [f"{i}\n{code(r['de'])} --> {code(r['a'])}\n{r['texte']}\n" for i, r in enumerate(voix["repliques"], 1)]
    chemin.parent.mkdir(exist_ok=True)
    chemin.write_text("\n".join(blocs), encoding="utf8")


if __name__ == "__main__":
    erreurs = [f"ecran · {e}" for e in controler_ecran()]
    a_l_ecran = mots(texte_a_l_ecran(SOURCE.read_text(encoding="utf8")))
    bilan = f"{a_l_ecran} mots a l'ecran"
    if VOIX.exists():
        voix = json.loads(VOIX.read_text(encoding="utf8"))
        erreurs += [f"voix  · {e}" for e in controler_voix(voix)]
        dits = sum(mots(r["texte"]) for r in voix["repliques"])
        parle = sum(r["a"] - r["de"] for r in voix["repliques"])
        bilan += f" · {dits} mots a la voix en {len(voix['repliques'])} repliques ({parle:.1f} s de parole sur {voix['duree']:.0f})"
        if "--detail" in sys.argv:
            for r in voix["repliques"]:
                besoin = duree_dite(r["texte"], voix["debit"]["syllabes_par_seconde"])
                print(f"  {r['repere']:5} {r['de']:5.1f}-{r['a']:4.1f} s  {syllabes(r['texte']):2} syll.  {besoin:.1f} s pour {r['a'] - r['de']:.1f} s  {r['texte']}")
        if "--sous-titres" in sys.argv:
            ecrire_sous_titres(voix, ICI / "sortie" / "voix.srt")
            bilan += " · sortie/voix.srt ecrit"
    for e in erreurs:
        print("ERREUR", e)
    print(f"{bilan} relus · {len(erreurs)} erreur(s)")
    sys.exit(1 if erreurs else 0)
