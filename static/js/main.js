/* ==========================================================================
   M UMAR Natural Remedies — main.js
   Handles: AOS init, navbar scroll/mobile menu, testimonial slider,
   flash auto-dismiss, delete confirmations, simple client-side validation.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  /* ---------------------------------------------------------------------
     AOS ANIMATIONS
  --------------------------------------------------------------------- */
  if (typeof AOS !== "undefined") {
    AOS.init({
      duration: 800,
      easing: "ease-out-cubic",
      once: true,
      offset: 80,
    });
  }

  /* ---------------------------------------------------------------------
     NAVBAR: scroll shadow effect
  --------------------------------------------------------------------- */
  const navbar = document.getElementById("navbar");
  if (navbar) {
    const toggleScrollClass = () => {
      if (window.scrollY > 24) {
        navbar.classList.add("scrolled");
      } else {
        navbar.classList.remove("scrolled");
      }
    };
    toggleScrollClass();
    window.addEventListener("scroll", toggleScrollClass);
  }

  /* ---------------------------------------------------------------------
     NAVBAR: mobile menu toggle
  --------------------------------------------------------------------- */
  const menuBtn = document.getElementById("mobile-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");
  const menuIconOpen = document.getElementById("icon-open");
  const menuIconClose = document.getElementById("icon-close");

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", function () {
      mobileMenu.classList.toggle("open");
      if (menuIconOpen && menuIconClose) {
        menuIconOpen.classList.toggle("hidden");
        menuIconClose.classList.toggle("hidden");
      }
    });

    // Close mobile menu when a link is tapped
    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.remove("open");
        if (menuIconOpen && menuIconClose) {
          menuIconOpen.classList.remove("hidden");
          menuIconClose.classList.add("hidden");
        }
      });
    });
  }

  /* ---------------------------------------------------------------------
     TESTIMONIALS SLIDER
  --------------------------------------------------------------------- */
  const slides = document.querySelectorAll(".testimonial-slide");
  const dots = document.querySelectorAll(".testimonial-dot");
  let currentSlide = 0;
  let sliderInterval = null;

  function showSlide(index) {
    if (!slides.length) return;
    slides.forEach((slide, i) => slide.classList.toggle("active", i === index));
    dots.forEach((dot, i) => dot.classList.toggle("active", i === index));
    currentSlide = index;
  }

  function nextSlide() {
    const next = (currentSlide + 1) % slides.length;
    showSlide(next);
  }

  function prevSlide() {
    const prev = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(prev);
  }

  function startAutoSlide() {
    sliderInterval = setInterval(nextSlide, 5500);
  }

  if (slides.length) {
    showSlide(0);
    startAutoSlide();

    dots.forEach((dot, i) => {
      dot.addEventListener("click", () => {
        clearInterval(sliderInterval);
        showSlide(i);
        startAutoSlide();
      });
    });

    const nextBtn = document.getElementById("testimonial-next");
    const prevBtn = document.getElementById("testimonial-prev");

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        clearInterval(sliderInterval);
        nextSlide();
        startAutoSlide();
      });
    }
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        clearInterval(sliderInterval);
        prevSlide();
        startAutoSlide();
      });
    }
  }

  /* ---------------------------------------------------------------------
     FLASH MESSAGES: auto-dismiss after 5 seconds
  --------------------------------------------------------------------- */
  const flashMessages = document.querySelectorAll(".flash-message");
  flashMessages.forEach((msg) => {
    setTimeout(() => {
      msg.style.transition = "opacity 0.5s ease";
      msg.style.opacity = "0";
      setTimeout(() => msg.remove(), 500);
    }, 5000);
  });

  /* ---------------------------------------------------------------------
     DELETE CONFIRMATION (appointments & products)
  --------------------------------------------------------------------- */
  document.querySelectorAll(".confirm-delete").forEach((form) => {
    form.addEventListener("submit", function (e) {
      const label = form.getAttribute("data-label") || "this item";
      const confirmed = window.confirm(`Are you sure you want to delete ${label}? This action cannot be undone.`);
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });

  /* ---------------------------------------------------------------------
     IMAGE PREVIEW for product add/edit forms
  --------------------------------------------------------------------- */
  const imageInput = document.getElementById("image");
  const imagePreview = document.getElementById("image-preview");

  if (imageInput && imagePreview) {
    imageInput.addEventListener("change", function () {
      const file = this.files && this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          imagePreview.src = e.target.result;
          imagePreview.classList.remove("hidden");
        };
        reader.readAsDataURL(file);
      }
    });
  }

  /* ---------------------------------------------------------------------
     CONTACT / APPOINTMENT FORM: minimal client-side validation
  --------------------------------------------------------------------- */
  const appointmentForm = document.getElementById("appointment-form");
  if (appointmentForm) {
    appointmentForm.addEventListener("submit", function (e) {
      const name = appointmentForm.querySelector("#name");
      const phone = appointmentForm.querySelector("#phone");
      const service = appointmentForm.querySelector("#service");
      const preferredDate = appointmentForm.querySelector("#preferred_date");
      let errorText = "";

      if (name && name.value.trim().length < 2) {
        errorText = "Please enter your full name.";
      } else if (phone && phone.value.trim().length < 7) {
        errorText = "Please enter a valid phone number.";
      } else if (service && !service.value) {
        errorText = "Please select a service.";
      } else if (preferredDate && !preferredDate.value) {
        errorText = "Please choose a preferred date.";
      }

      const errorBox = document.getElementById("form-client-error");
      if (errorText) {
        e.preventDefault();
        if (errorBox) {
          errorBox.textContent = errorText;
          errorBox.classList.remove("hidden");
        }
      } else if (errorBox) {
        errorBox.classList.add("hidden");
      }
    });
  }

  /* ---------------------------------------------------------------------
     Set minimum date for appointment date picker to today
  --------------------------------------------------------------------- */
  const dateInput = document.getElementById("preferred_date");
  if (dateInput) {
    const today = new Date().toISOString().split("T")[0];
    dateInput.setAttribute("min", today);
  }

});
