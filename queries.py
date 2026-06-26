import json
import psycopg2
import psycopg2.extras
import dash_leaflet.express as dlx

from config import (
    DB_NAME,
    DB_USER,
    DB_HOST,
    DB_PORT,
    EVENT_ID_DATASET,
    ID_COMMUNE,
)


def connect():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn, cursor


def filter_by_column(sql, column, filter, parameters={}):
    sql += f" AND {column} = %({column})s "
    parameters[column] = filter
    return sql, parameters


def get_total_obs(column=None, filter=None):
    conn, cursor = connect()

    sql = """
        SELECT count(*) 
        FROM gn_synthese.synthese
        JOIN taxonomie.taxref USING(cd_nom)
        WHERE id_dataset = %(event_id_dataset)s
    """
    parameters = {"event_id_dataset": EVENT_ID_DATASET}
    if column and filter:
        sql, parameters = filter_by_column(sql, column, filter, parameters)
    cursor.execute(sql, parameters)
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data[0]


def species_as_dict(row):
    d = dict(row)
    cd_ref = row["cd_ref"]
    lb_nom = row["lb_nom"]
    d["lb_nom"] = (
        f" <a target='_blank' href='https://atlas.mercantour.eu/espece/{cd_ref}'> {lb_nom} </a>"
    )
    return d


def get_new_species():

    conn, cursor = connect()

    sql = """
    select distinct t.cd_ref, t.lb_nom, t.group2_inpn, t.group3_inpn, t.regne, t.ordre, t.famille, string_agg(distinct observers, ', ') as observateurs
    from gn_synthese.synthese s 
    join taxonomie.taxref t using(cd_nom)
    LEFT JOIN (
        select distinct t2.cd_ref
        from gn_synthese.synthese s2
        join taxonomie.taxref t2 ON s2.cd_nom = t2.cd_nom
        where id_dataset!=%(id_explore)s
    ) as exist ON exist.cd_ref = t.cd_ref 
    where id_dataset=%(id_explore)s and exist.cd_ref is null AND (t.id_rang = 'ES' OR t.id_rang = 'SSES')
    group by t.cd_ref, t.lb_nom, t.group2_inpn, t.group3_inpn, t.regne, t.ordre, t.famille

    """
    cursor.execute(sql, {"id_explore": EVENT_ID_DATASET})
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [species_as_dict(d) for d in data]


def get_new_species_commune():

    conn, cursor = connect()

    sql = """
    select t.cd_ref, t.lb_nom, t.group2_inpn, t.group3_inpn, t.regne, t.ordre, t.famille, string_agg(distinct observers, ', ') as observateurs
    from gn_synthese.synthese s 
    join taxonomie.taxref t using(cd_nom)
    left join (
	    select distinct t2.cd_ref
	    from gn_synthese.synthese s2
	    join taxonomie.taxref t2 using(cd_nom)
	    where id_dataset!=%(id_explore)s AND EXISTS (
	        SELECT id_synthese
	        FROM gn_synthese.cor_area_synthese cor
	        WHERE id_area = %(id_commune)s and cor.id_synthese = s2.id_synthese
	    )
    ) exist on exist.cd_ref = t.cd_ref
   where id_dataset=%(id_explore)s and exist.cd_ref is null AND (t.id_rang = 'ES' OR t.id_rang = 'SSES')
    group by t.cd_ref, t.lb_nom, t.group2_inpn, t.group3_inpn, t.regne, t.ordre, t.famille
    order by lb_nom asc
    """
    cursor.execute(sql, {"id_explore": EVENT_ID_DATASET, "id_commune": ID_COMMUNE})
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [species_as_dict(d) for d in data]


def get_all_data_geo(column=None, filter=None):
    conn, cursor = connect()

    sql = """
        SELECT lb_nom, observers, cd_ref, st_x(the_geom_point) as lon,
        st_y(the_geom_point) as lat,
        1 as nb
        FROM gn_synthese.synthese
         JOIN taxonomie.taxref USING(cd_nom)
        WHERE id_dataset = %(event_id_dataset)s
    """
    parameters = {"event_id_dataset": EVENT_ID_DATASET}
    if column and filter:
        sql, parameters = filter_by_column(sql, column, filter, parameters)

    sql += " LIMIT 5000"

    cursor.execute(sql, parameters)
    data = cursor.fetchall()

    geojson = dlx.dicts_to_geojson(data)
    cursor.close()
    conn.close()

    return geojson


def get_species_in_event():
    conn, cursor = connect()
    sql = """
        select  lb_nom, cd_ref, group2_inpn, group3_inpn, regne, ordre, famille, count(s.*) as nb_obs, string_agg(distinct observers, ', ') as observateurs
        from gn_synthese.synthese s 
        join taxonomie.taxref t using(cd_nom)
        where id_dataset=%(id_explore)s AND (t.id_rang = 'ES' OR t.id_rang = 'SSES')
        GROUP BY lb_nom, cd_ref, group2_inpn, group3_inpn, regne, ordre, famille
        order by lb_nom ASC
    """
    parameters = {"id_explore": EVENT_ID_DATASET}

    cursor.execute(sql, parameters)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [species_as_dict(d) for d in data]


def get_group2_inpn():
    conn, cursor = connect()

    sql = """
        SELECT distinct group2_inpn
        FROM taxonomie.taxref
        JOIN gn_synthese.synthese USING(cd_nom)
        where id_dataset=%(id_explore)s
        order by group2_inpn ASC
    """
    cursor.execute(sql, {"id_explore": EVENT_ID_DATASET})
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [d[0] for d in data]


def get_group3_inpn(group2_inpn=None):
    conn, cursor = connect()

    sql = """
        SELECT distinct group3_inpn
        FROM taxonomie.taxref
        JOIN gn_synthese.synthese USING(cd_nom)
        where id_dataset=%(id_explore)s
    """
    parameters = {"id_explore": EVENT_ID_DATASET}
    if group2_inpn:
        sql += " AND group2_inpn = %(group2_inpn)s"
        parameters["group2_inpn"] = group2_inpn

    sql += " order by group3_inpn ASC"

    cursor.execute(sql, parameters)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [d[0] for d in data if d[0]]


def get_ordres():
    conn, cursor = connect()

    sql = """
        SELECT distinct ordre
        FROM taxonomie.taxref
        JOIN gn_synthese.synthese USING(cd_nom)
        where id_dataset=%(id_explore)s
        order by ordre ASC
    """
    cursor.execute(sql, {"id_explore": EVENT_ID_DATASET})
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [d[0] for d in data]


def get_familles():
    conn, cursor = connect()

    sql = """
        SELECT distinct famille
        FROM taxonomie.taxref
        JOIN gn_synthese.synthese USING(cd_nom)
        where id_dataset=%(id_explore)s
        order by famille ASC
    """
    cursor.execute(sql, {"id_explore": EVENT_ID_DATASET})
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return [d[0] for d in data]


def get_observers():
    conn, cursor = connect()

    sql = """
    select distinct concat(tr.nom_role, ' ', tr.prenom_role) as observateurs
    from gn_synthese.synthese s 
    join gn_synthese.cor_observer_synthese using(id_synthese)
    join utilisateurs.t_roles tr using(id_role)
    where s.id_dataset=%(id_explore)s
    """
    cursor.execute(sql, {"id_explore": EVENT_ID_DATASET})
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return [dict(d) for d in data]


def get_communal_limit():
    conn, cursor = connect()

    sql = """
    select st_asgeojson(geom_4326)
    from ref_geo.l_areas la 
    where id_area = %(id_commune)s;
    """
    cursor.execute(sql, {"id_commune": ID_COMMUNE})
    data = cursor.fetchone()
    feature = {"type": "Feature", "geometry": json.loads(data[0])}
    cursor.close()
    conn.close()

    geojson = {"type": "FeatureCollection", "features": [feature]}

    return geojson


import numpy as np

def get_bounds(geojson):
    coords = []

    for feature in geojson["features"]:
        geom = feature["geometry"]

        if geom["type"] == "Point":
            coords.append(geom["coordinates"])

        elif geom["type"] in ["LineString", "MultiPoint"]:
            coords.extend(geom["coordinates"])

        elif geom["type"] in ["Polygon", "MultiLineString"]:
            for part in geom["coordinates"]:
                coords.extend(part)

        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                for part in polygon:
                    coords.extend(part)

    coords = np.array(coords)
    lons = coords[:, 0]
    lats = coords[:, 1]

    return [[lats.min(), lons.min()], [lats.max(), lons.max()]]


def get_communal_bounds():
    conn, cursor = connect()

    sql = """
    select st_asgeojson(st_envelope(geom_4326))
    from ref_geo.l_areas la 
    where id_area = %(id_commune)s;
    """
    cursor.execute(sql, {"id_commune": ID_COMMUNE})
    data = cursor.fetchone()
    feature = {"type": "Feature", "geometry": json.loads(data[0])}
    cursor.close()
    conn.close()

    geojson = {"type": "FeatureCollection", "features": [feature]}

    return get_bounds(geojson)