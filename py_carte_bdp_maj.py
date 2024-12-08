from flask import Flask, render_template, request, send_file
import geopandas as gpd
from shapely.geometry import Point
import os

app = Flask(__name__)

# Répertoire temporaire pour les fichiers SHP
TEMP_DIR = "temp_shp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Données collectées (simples pour l'exemple)
user_data = []

# Route pour afficher la carte interactive
@app.route("/")
def index():
    # Carte Folium centrée sur un point par défaut
    map_object = folium.Map(location=[48.8566, 2.3522], zoom_start=12)  # Paris
    for data in user_data:
        folium.Marker(location=data["coords"], popup=data["name"]).add_to(map_object)
    map_html = map_object._repr_html_()
    return render_template("index.html", map_html=map_html)

# Route pour soumettre des données via formulaire
@app.route("/submit_data", methods=["POST"])
def submit_data():
    name = request.form["name"]
    lat = float(request.form["latitude"])
    lon = float(request.form["longitude"])
    user_data.append({"name": name, "coords": (lat, lon)})
    return "Données ajoutées avec succès ! <a href='/'>Retour</a>"

# Route pour générer et télécharger le fichier SHP
@app.route("/generate_shp", methods=["GET"])
def generate_shp():
    if not user_data:
        return "Aucune donnée disponible pour générer un SHP. <a href='/'>Retour</a>"

    # Créer un GeoDataFrame avec les données collectées
    gdf_data = {
        "Name": [d["name"] for d in user_data],
        "geometry": [Point(d["coords"][1], d["coords"][0]) for d in user_data],
    }
    gdf = gpd.GeoDataFrame(gdf_data, crs="EPSG:4326")

    # Chemin pour enregistrer le SHP
    shp_path = os.path.join(TEMP_DIR, "data.shp")
    gdf.to_file(shp_path, driver="ESRI Shapefile")

    return send_file(shp_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
