// Client-side behaviors for the alumni update form.
//
// Notes:
// - Input `name` attributes are expected to be snake_case and match the
//   WTForms/Flask session keys used server-side (e.g. `geneva_degrees`,
//   `spouse_geneva_degrees`, `volunteer_radio`). Keep those in sync when
//   updating forms or templates.
// - This file provides small UI helpers only (show/hide fields, image
//   resizing, add/remove birth sections). It does not change form data
//   submission semantics.
//
// reveal "other" option if chosen on volunteer dropdown
document.addEventListener("DOMContentLoaded", function () {
  const other_checkboxes = document.querySelectorAll('input[type="checkbox"]');
  const other_container = document.getElementById("other_volunteer_container");

  function toggle_other_field() {
    let is_other_selected = false;

    other_checkboxes.forEach(function(checkbox) {
      if (checkbox.value.toLowerCase() === "other" && checkbox.checked) {
        is_other_selected = true;
      }
    });

    if (other_container) {
      other_container.style.display = is_other_selected ? 'block' : 'none';
    }
  }

  // Add event listeners to all checkboxes
  other_checkboxes.forEach(function(checkbox) {
    checkbox.addEventListener("change", toggle_other_field);
  });

  // Initial check on page load
  toggle_other_field();
});

// reveal field for spouse's grad year if option "yes" selected
document.addEventListener("DOMContentLoaded", function () {
    const spouse_grad_radios = document.querySelectorAll(
      'input[name="spouse_geneva_grad"]'
    );

    const spouse_grad_year_field = document.getElementById("spouseGradYearContainer");

    function toggle_spouse_grad_year() {
      const selected = document.querySelector(
        'input[name="spouse_geneva_grad"]:checked'
      );

      if (selected && selected.value === "Yes") {
        spouse_grad_year_field.style.display = "block";
      } else {
        spouse_grad_year_field.style.display = "none";
      }
    }

    spouse_grad_radios.forEach(radio => {
      radio.addEventListener("change", toggle_spouse_grad_year);
    });

    // Handle page refresh / pre-populated values
    toggle_spouse_grad_year();
});

// repeatable birth annoucemnet section 
let birth_section_count = 0;

function add_birth_section() {
  birth_section_count++;

  const template = document.querySelector(".birth-announcement-template");
  const clone = template.cloneNode(true);
  clone.style.display = "block";

  // Update all input fields to use unique names/IDs
  const inputs = clone.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    if (input.name) {
      // Handle array-style fields
      if (input.name.includes("[]")) {
        input.name = input.name.replace("[]", `[${birth_section_count}]`);
      }

      // Handle gender radios specifically
      if (input.name.startsWith("AlumniChildGender")) {
        input.name = `AlumniChildGender_${birth_section_count}`;
      }
    }

    // Reset input values
    if (input.type === "radio" || input.type === "checkbox") {
      input.checked = false;
    } else {
      input.value = "";
    }
  });

  // Append to container
  document.getElementById("children-container").appendAlumniChild(clone);
}

function remove_birth_section(button) {
  const section = button.closest(".birth-announcement-group");
  if (section) {
    section.remove();
  }
}

// image drag and drop 
  document.addEventListener('DOMContentLoaded', function () {
  const drop_zone = document.getElementById('drop-zone');
  const image_input = document.getElementById('image-input');
  const canvas = document.getElementById('preview-canvas');
  const hidden_input = document.getElementById('resized-image');

  const max_width = 600;   // Desired width
  const max_height = 400;  // Desired height

  drop_zone.addEventListener('click', () => image_input.click());

  drop_zone.addEventListener('dragover', (e) => {
    e.preventDefault();
  drop_zone.classList.add('hover');
  });

  drop_zone.addEventListener('dragleave', () => {
    drop_zone.classList.remove('hover');
  });

  drop_zone.addEventListener('drop', (e) => {
    e.preventDefault();
  drop_zone.classList.remove('hover');
  const file = e.dataTransfer.files[0];
  handle_image(file);
  });

  image_input.addEventListener('change', () => {
    const file = image_input.files[0];
  handle_image(file);
  });

  function handle_image(file) {
    if (!file || !file.type.startsWith('image/')) return;

  const reader = new FileReader();
  reader.onload = function (event) {
      const img = new Image();
  img.onload = function () {
        const ratio = Math.min(max_width / img.width, max_height / img.height);
  const width = img.width * ratio;
  const height = img.height * ratio;

  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, width, height);
  ctx.drawImage(img, 0, 0, width, height);

        // Convert canvas to base64
        canvas.toBlob((blob) => {
          const reader = new FileReader();
          reader.onloadend = () => {
    hidden_input.value = reader.result;  // Base64 encoded image
          };
  reader.readAsDataURL(blob);
        }, 'image/jpeg', 0.85);  // JPEG with 85% quality
      };
  img.src = event.target.result;
    };
  reader.readAsDataURL(file);
  }
});

// prev and next buttons
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const nav_buttons = document.querySelectorAll("button[name='nav']");

  nav_buttons.forEach(button => {
    button.addEventListener("click", function () {
      // Mark which button was clicked
      const action = this.value;

      // Create or update a hidden input to submit the action

      let nav_input = document.querySelector("input[name='nav']");
      if (!nav_input) {
        nav_input = document.createElement("input");
        nav_input.type = "hidden";
        nav_input.name = "nav";
        form.appendAlumniChild(nav_input);
      }

      nav_input.value = action;

      // Optionally disable the buttons after click
      nav_buttons.forEach(btn => btn.disabled = true);

      // Submit the form manually
      form.submit();
    });
  });

  document.addEventListener("DOMContentLoaded", function () {
    const imageUrl = "{{ image_url }}";
    if (imageUrl) {
      const preview = document.getElementById("image-preview");
      if (preview) {
        const img = document.createElement("img");
        img.src = imageUrl;
        img.style.maxWidth = "100%";
        preview.innerHTML = "";
        preview.appendAlumniChild(img);
      }
    }
  });
});
