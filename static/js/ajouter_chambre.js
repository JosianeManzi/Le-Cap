function validerType() {
    const type = document.getElementById("type_chambre").value.trim();
    const msg = document.getElementById("erreur-type");
    msg.textContent = "";
    if (!type) {
        msg.textContent = "Le type de chambre est requis.";
        return false;
    }
    return true;
}


function validerDescription() {
    const description = document.getElementById("description").value.trim();
    const msg = document.getElementById("erreur-description");
    msg.textContent = "";
    if (!description) {
        msg.textContent = "La description est requise.";
        return false;
    }
    return true;
}


function validerPrix() {
    const prix = document.getElementById("prix_nuit").value.trim();
    const msg = document.getElementById("erreur-prix");
    msg.textContent = "";
    if (!prix || isNaN(prix) || Number(prix) <= 0) {
        msg.textContent = "Le prix doit être un nombre positif.";
        return false;
    }
    return true;
}


async function ajouterChambre(e) {
    e.preventDefault();

    const typeValide = validerType();
    const descriptionValide = validerDescription();
    const prixValide = validerPrix();
    const imageValide = validerImage();

    if (!typeValide || !descriptionValide || !prixValide || !imageValide) {
        return false;
    }

    const form = document.getElementById("form-ajouter-chambre");
    const donnees = new FormData(form);

    if (!document.getElementById("disponible").checked) {
        donnees.set("disponible", "0");
    }

    try {
        const reponse = await fetch("/chambres/ajouter_chambre", {
            method: "POST",
            body: donnees
        });

        const resultat = await reponse.json();

        if (!reponse.ok) {
            throw new Error(resultat.message || "Erreur serveur.");
        }

        alert(resultat.message);
        form.reset();
        return true;

    } catch (err) {
        alert("Erreur lors de l'ajout de la chambre.");
        return false;
    }
}
function validerImage() {
    const fichier = document.getElementById("image").files[0];
    const msg = document.getElementById("erreur-image");
    msg.textContent = "";
    if (!fichier) {
        msg.textContent = "L'image est obligatoire.";
        return false;
    }
    if (!fichier.type.startsWith("image/")) {
        msg.textContent = "Le fichier doit être une image.";
        return false;
    }
    return true;
}

function initialiserValidation() {
    document.getElementById("type_chambre").addEventListener("input", validerType);
    document.getElementById("description").addEventListener("input", validerDescription);
    document.getElementById("prix_nuit").addEventListener("input", validerPrix);
    document.getElementById("form-ajouter-chambre").addEventListener("submit", ajouterChambre);
    document.getElementById("image").addEventListener("change", validerImage);
    return true;
}
window.addEventListener("load", initialiserValidation);