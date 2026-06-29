document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".add-to-cart-form").forEach(form => {
    form.addEventListener("submit", function(e) {
      e.preventDefault();

      const url = form.action;
      const formData = new FormData(form);

      fetch(url, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
      .then(response => response.json())
      .then(data => {
        // ✅ Message global en haut
        const globalMsg = document.getElementById("global-message");
        globalMsg.innerHTML = `<div class="alert alert-success text-center">${data.message}</div>`;

        // Supprimer après 3 secondes
        setTimeout(() => {
          globalMsg.innerHTML = "";
        }, 3000);

        // ✅ Mettre à jour les compteurs panier si présents
        document.querySelectorAll(".cart-count").forEach(cartCounter => {
          cartCounter.textContent = data.cart_count;
        });
      })
      .catch(error => console.error("Erreur AJAX:", error));
    });
  });
});
