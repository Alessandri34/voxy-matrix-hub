<?php
/**
 * Réception des formulaires VFormations.
 * Enregistre chaque demande dans un fichier hors racine web, puis notifie
 * par e-mail. L'enregistrement prime : si l'e-mail échoue, la demande est
 * conservée malgré tout.
 */
declare(strict_types=1);

const NOTIFY_TO   = 'contact@vformations.fr';
const JOURNAL     = __DIR__ . '/../private/demandes.csv';
const LIMITE_IP   = 5;      // demandes max
const LIMITE_SEC  = 3600;   // par heure

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

function repondre(int $code, array $corps): never {
    http_response_code($code);
    echo json_encode($corps, JSON_UNESCAPED_UNICODE);
    exit;
}

/** Neutralise les retours ligne : empêche l'injection d'en-têtes e-mail. */
function propre(string $v, int $max = 2000): string {
    $v = str_replace(["\r", "\n", "\0"], ' ', $v);
    return mb_substr(trim($v), 0, $max);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    repondre(405, ['ok' => false, 'error' => 'methode_non_autorisee']);
}

// Pot de miel : rempli = robot, on acquiesce sans rien enregistrer.
if (!empty($_POST['_gotcha'])) {
    repondre(200, ['ok' => true]);
}

$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';

// Limitation par IP
$seau = sys_get_temp_dir() . '/vf_' . hash('sha256', $ip) . '.txt';
$horodatages = is_readable($seau)
    ? array_filter(array_map('intval', explode(',', (string) file_get_contents($seau))))
    : [];
$horodatages = array_values(array_filter($horodatages, fn($t) => $t > time() - LIMITE_SEC));
if (count($horodatages) >= LIMITE_IP) {
    repondre(429, ['ok' => false, 'error' => 'trop_de_demandes']);
}
$horodatages[] = time();
@file_put_contents($seau, implode(',', $horodatages), LOCK_EX);

// Champs attendus
$champs = ['nom', 'email', 'tel', 'activite', 'sujet', 'besoin',
           'financeur', 'message', 'consentement', '_form', '_page'];
$d = [];
foreach ($champs as $c) {
    $d[$c] = propre((string) ($_POST[$c] ?? ''));
}

// Validation minimale
if ($d['nom'] === '' || $d['message'] === '') {
    repondre(400, ['ok' => false, 'error' => 'champs_obligatoires']);
}
if (!filter_var($d['email'], FILTER_VALIDATE_EMAIL)) {
    repondre(400, ['ok' => false, 'error' => 'email_invalide']);
}

$quand = date('d/m/Y H:i:s');

// ── 1. Enregistrement (prioritaire sur l'e-mail) ──────────────────────────
$dossier = dirname(JOURNAL);
if (!is_dir($dossier)) { @mkdir($dossier, 0750, true); }

$nouveau = !file_exists(JOURNAL);
$fh = @fopen(JOURNAL, 'a');
$enregistre = false;
if ($fh !== false) {
    if (flock($fh, LOCK_EX)) {
        if ($nouveau) {
            fputcsv($fh, ['Date', 'Formulaire', 'Nom', 'E-mail', 'Telephone',
                          'Activite', 'Sujet', 'Besoin', 'Financeur', 'Message',
                          'Consentement', 'Page', 'IP'], ';');
        }
        fputcsv($fh, [$quand, $d['_form'], $d['nom'], $d['email'], $d['tel'],
                      $d['activite'], $d['sujet'], $d['besoin'], $d['financeur'],
                      $d['message'], $d['consentement'], $d['_page'], $ip], ';');
        fflush($fh);
        flock($fh, LOCK_UN);
        $enregistre = true;
    }
    fclose($fh);
}

// ── 2. Notification ───────────────────────────────────────────────────────
$libelle = $d['_form'] === 'diagnostic' ? 'Demande de diagnostic' : 'Message de contact';
$sujet   = '[VFormations] ' . $libelle . ($d['nom'] !== '' ? ' - ' . $d['nom'] : '');

$lignes = [$libelle . ' reçu le ' . $quand, ''];
$etiquettes = ['nom' => 'Nom', 'email' => 'E-mail', 'tel' => 'Téléphone',
    'activite' => 'Activité', 'sujet' => 'Sujet', 'besoin' => 'Besoin',
    'financeur' => 'Financeur', 'message' => 'Message',
    'consentement' => 'Consentement RGPD', '_page' => 'Page'];
foreach ($etiquettes as $c => $lib) {
    if ($d[$c] !== '') { $lignes[] = $lib . ' : ' . $d[$c]; }
}
$lignes[] = '';
$lignes[] = '— Notification automatique du site vformations.fr';

// L'expéditeur reste sur un domaine que ce serveur est autorisé à utiliser :
// le SPF de vformations.fr ne couvre que Google, pas ce VPS.
$expediteur = 'no-reply@' . ($_SERVER['SERVER_NAME'] ?? 'localhost');
$entetes = [
    'From: Site VFormations <' . $expediteur . '>',
    'Reply-To: ' . ($d['nom'] !== '' ? $d['nom'] . ' <' . $d['email'] . '>' : $d['email']),
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: VFormations',
];
$envoye = @mail(NOTIFY_TO, '=?UTF-8?B?' . base64_encode($sujet) . '?=',
                implode("\n", $lignes), implode("\r\n", $entetes));

if (!$enregistre && !$envoye) {
    repondre(500, ['ok' => false, 'error' => 'enregistrement_impossible']);
}
repondre(200, ['ok' => true, 'enregistre' => $enregistre, 'notifie' => $envoye]);
