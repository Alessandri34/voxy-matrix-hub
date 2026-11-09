# Modele Hestia HTTP du back-office — a installer dans
# /usr/local/hestia/data/templates/web/nginx/backoffice.tpl
#
# Il ne sert rien : il renvoie tout en HTTPS. Le back-office ne doit jamais
# repondre en clair, il ne contient que des donnees de prospects.
# Seule exception : /.well-known/acme-challenge/, sans quoi Let's Encrypt
# ne peut pas renouveler le certificat — et un renouvellement rate coupe
# l'acces au back-office au bout de 90 jours.

server {
    listen      %ip%:%web_port%;
    server_name %domain_idn% %alias_idn%;

    access_log /var/log/nginx/domains/%domain%.log combined;
    error_log  /var/log/nginx/domains/%domain%.error.log error;

    location ^~ /.well-known/acme-challenge/ {
        root %docroot%;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }

    include %home%/%user%/conf/web/%domain%/nginx.conf_*;
}
