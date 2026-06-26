def format_columns(data, html_cols=["lb_nom"]):
    if data and len(data) > 0:
        first_row = data[0]
        cols = []
        for col in first_row.keys():

            col_def = {"id": col, "name": col}
            if col in html_cols:
                col_def["presentation"] = "markdown"
            cols.append(col_def)
        return cols
    return None


# pointToLayer = """
#     function (feature, latlng) {
#         return L.circleMarker(latlng);
#     }
# """


pointToLayer = """
function(feature, latlng){
    const marker = L.circleMarker(latlng);

    const props = feature.properties;

    const content = `
        <b>${props.lb_nom}</b>
        <br>${props.observers}</br>
        <a href="https://atlas.mercantour.eu/espece/${props.cd_ref}" target='_blank'>Voir la fiche de l'espece</a>
    `;

    marker.bindPopup(content);
    return marker;
}
"""