/**
 * Marina Serenella - Core Client Utilities, Email Protection & Cookie Banner
 */
(function () {
  function revealEmails() {
    var elements = document.querySelectorAll(".js-email");
    elements.forEach(function (el) {
      var user = el.getAttribute("data-u");
      var domain = el.getAttribute("data-d");
      if (user && domain) {
        var email = user + "@" + domain;
        el.href = "mailto:" + email;
        el.textContent = email;
      }
    });
  }

  function initCookieBanner() {
    if (localStorage.getItem("cookie_consent_choice")) {
      return; // User has already responded
    }

    var lang = document.documentElement.lang || "it";
    var isSubdir = lang !== "it";
    var policyLink = (isSubdir ? "../" : "") + "cookie-policy.html";

    var contentMap = {
      it: {
        text: 'Questo sito utilizza solo cookie tecnici essenziali per la navigazione e la preferenza della lingua. Consulta la <a href="' + policyLink + '">Cookie Policy</a> per dettagli.',
        btn: "Ho capito"
      },
      en: {
        text: 'This website uses only essential technical cookies for navigation and language preferences. Read our <a href="' + policyLink + '">Cookie Policy</a> for details.',
        btn: "Got it"
      },
      de: {
        text: 'Diese Website verwendet nur essenzielle technische Cookies für Navigation und Sprachauswahl. Lesen Sie unsere <a href="' + policyLink + '">Cookie-Richtlinie</a>.',
        btn: "Verstanden"
      },
      fr: {
        text: 'Ce site utilise uniquement des cookies techniques essentiels pour la navigation et la langue. Consultez notre <a href="' + policyLink + '">Politique de Cookies</a>.',
        btn: "J'ai compris"
      }
    };

    var i18n = contentMap[lang] || contentMap.it;

    var banner = document.createElement("div");
    banner.className = "cookie-banner";
    banner.innerHTML =
      '<p>' + i18n.text + '</p>' +
      '<div class="cookie-actions">' +
        '<button type="button" class="btn btn-primary" id="btn-accept-cookie">' + i18n.btn + '</button>' +
      '</div>';

    document.body.appendChild(banner);

    setTimeout(function () {
      banner.classList.add("active");
    }, 250);

    function closeBanner() {
      localStorage.setItem("cookie_consent_choice", "acknowledged");
      banner.classList.remove("active");
      setTimeout(function () {
        if (banner.parentNode) {
          banner.parentNode.removeChild(banner);
        }
      }, 450);
    }

    document.getElementById("btn-accept-cookie").addEventListener("click", closeBanner);
  }

  function init() {
    revealEmails();
    initCookieBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
