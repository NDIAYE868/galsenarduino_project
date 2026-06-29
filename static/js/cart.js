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
        // ✅ Message global en haut (remplace directement l'ancien message et dure 2 secondes)
        const globalMsg = document.getElementById("global-message");
        
        // Vider le message précédent immédiatement
        globalMsg.innerHTML = "";
        
        const alertDiv = document.createElement("div");
        alertDiv.className = "galsen-alert animate__animated animate__slideInDown";
        alertDiv.setAttribute("role", "alert");
        alertDiv.innerHTML = `
          <div class="d-flex align-items-center">
            <i class="bi bi-check-circle-fill text-warning me-3 fs-5"></i>
            <span class="fw-semibold text-white">${data.message}</span>
          </div>
          <button type="button" class="btn-close ms-3" aria-label="Close" onclick="this.parentElement.remove()"></button>
        `;
        
        globalMsg.appendChild(alertDiv);

        // Supprimer l'alerte après 3 secondes avec animation
        setTimeout(() => {
            alertDiv.classList.remove("animate__slideInDown");
            alertDiv.classList.add("animate__fadeOutUp");

            alertDiv.addEventListener("animationend", () => {
                alertDiv.remove();
            }, { once: true });
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
