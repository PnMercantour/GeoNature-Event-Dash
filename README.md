Tableau de bord GeoNature avec Dash
===================================

Application issue d'un Fork du projet https://github.com/PnEcrins/GeoNature-Event-Dash du Parc national de Ecrins

Cette application permet de générer un tableau de bord de données en se connectant à une base de données GeoNature.
Elle a été utilisée pour restituer en continu et en temps réel les données lors d'un évenement naturaliste : Explor'Nature.

Elle affiche les données d'un jeu de données et d'un zonage géographique comme une commune ou autre (configurable dans le fichier `config.py`) avec les éléments suivants :

- tableau des espèces
- tableau des nouvelles espèces pour la commune
- tableau des nouvelles espèce pour la structure
- graphique de répartition des nouvelles espèces
- carte des observations

Tous les éléments sont filtrables par groupe2 INPN, groupe3 INPN, ordre et famille.

Organisation du style
=====================

La configuration de style est séparée en deux couches pour faciliter la réutilisation.

- `assets/00_style_config.css` : variables CSS globales (couleurs, typo, rayons, ombres, espacements)
- `assets/theme.css` : règles de mise en page qui utilisent ces variables

Les styles Python du dashboard (tables et graphiques) sont centralisés dans le fichier `style_config.py`.

- `TABLE_STYLE_CELL`, `TABLE_STYLE_HEADER`, `TABLE_STYLE_DATA`
- `style_pie_chart(fig, title)`
- `HERO_TITLE_TEXT`, `HERO_KICKER_TEXT`, `HERO_SUBTITLE_TEXT`, `HERO_LOGO_SRC`, `HERO_LOGO_ALT`

Cette application est entièrement basée sur l'outil Python [Dash](https://dash.plotly.com/) et vous pouvez l'adapter à votre contexte ou le compléter avec les requêtes et restitutions que vous souhaitez.

![Aperçu](docs/GeoNature-event-dash-preview.jpg)

Installation et lancement
=========================

    # Télécharger ou cloner le dépôt
    # Installer les dépendances
    pip install -r requirements.in
    # désampler le fichier de config et le remplir
    cp config.py.sample config.py
    # Lancer l'application  (par défaut disponible sur : http://127.0.0.1:8050/ )
    python dash_app.py
