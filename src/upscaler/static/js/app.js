let uploadedImageData = null;
let currentMode = "pixel";
let originalImageFile = null;
let originalImageDimensions = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initializeDragAndDrop();
  initializeForm();
});

// Drag and drop functionality
function initializeDragAndDrop() {
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("image");

  // Click to select file
  dropArea.addEventListener("click", () => {
    fileInput.click();
  });

  // File input change
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });

  // Prevent default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Highlight drop area when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, () => {
      dropArea.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, () => {
      dropArea.classList.remove("dragover");
    });
  });

  // Handle dropped files
  dropArea.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      handleFile(files[0]);
    }
  });
}

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function handleFile(file) {
  if (!file.type.startsWith("image/")) {
    showStatus("error", "Please select a valid image file.");
    return;
  }

  originalImageFile = file;

  // Update drop area text
  const dropText = document.querySelector(".drop-text");
  dropText.textContent = `✓ ${file.name}`;

  // Show original image preview
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      // Store original dimensions
      originalImageDimensions = {
        width: img.width,
        height: img.height,
      };

      // Calculate DPI (assume 96 DPI as default for web images)
      const dpi = 96;

      // Show original image
      const originalImg = document.getElementById("originalImg");
      originalImg.src = e.target.result;

      // Update image info
      document.getElementById("originalDimensions").textContent =
        `${img.width} × ${img.height} px`;
      document.getElementById("originalDpi").textContent = `${dpi} DPI`;

      // Show original preview container
      document.getElementById("originalPreview").style.display = "block";

      // Hide upscaled preview
      document.getElementById("upscaledPreview").style.display = "none";
      document.querySelector(".download-btn-container").style.display = "none";
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function switchMode(mode) {
  currentMode = mode;
  const pixelMode = document.getElementById("pixelMode");
  const cmMode = document.getElementById("cmMode");
  const pixelBtn = document.getElementById("pixelModeBtn");
  const cmBtn = document.getElementById("cmModeBtn");

  if (mode === "pixel") {
    pixelMode.classList.add("active");
    cmMode.classList.remove("active");
    pixelBtn.classList.add("active");
    cmBtn.classList.remove("active");
  } else {
    pixelMode.classList.remove("active");
    cmMode.classList.add("active");
    pixelBtn.classList.remove("active");
    cmBtn.classList.add("active");
  }
}

function initializeForm() {
  document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!originalImageFile) {
      showStatus("error", "Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", originalImageFile);

    if (currentMode === "pixel") {
      const width = document.getElementById("width").value;
      const height = document.getElementById("height").value;
      formData.append("target_width", width);
      formData.append("target_height", height);
    } else {
      const widthCm = document.getElementById("widthCm").value;
      const heightCm = document.getElementById("heightCm").value;
      const dpi = document.getElementById("dpi").value;
      formData.append("width_cm", widthCm);
      formData.append("height_cm", heightCm);
      formData.append("dpi", dpi);
    }

    const statusDiv = document.getElementById("status");
    const submitBtn = document.getElementById("submitBtn");
    const upscaledPreview = document.getElementById("upscaledPreview");

    // Show loading state
    statusDiv.style.display = "block";
    statusDiv.className = "info";
    statusDiv.textContent = "Upscaling image... This may take a moment.";
    submitBtn.disabled = true;

    // Show upscaled preview container with loading animation
    upscaledPreview.style.display = "block";

    const upscaledWrapper = document.querySelector("#upscaledPreview .image-wrapper");
    upscaledWrapper.innerHTML = `
      <div class="loading-pulse" style="text-align: center; padding: 40px;">
        <div style="font-size: 3rem; color: #4caf50; margin-bottom: 10px;">⏳</div>
        <div style="color: #666;">Processing...</div>
      </div>
      <div class="loading-shimmer"></div>
    `;

    try {
      const response = await fetch("/upscale", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to upscale image");
      }

      const blob = await response.blob();
      uploadedImageData = blob;
      const imageUrl = URL.createObjectURL(blob);

      // Load the upscaled image to get dimensions
      const img = new Image();
      img.onload = () => {
        // Update upscaled image
        upscaledWrapper.innerHTML = `<img id="upscaledImg" src="${imageUrl}" alt="Upscaled image" />`;

        // Calculate DPI (assume 96 DPI as default)
        const dpi = 96;

        // Update image info
        document.getElementById("upscaledDimensions").textContent =
          `${img.width} × ${img.height} px`;
        document.getElementById("upscaledDpi").textContent = `${dpi} DPI`;

        // Show download button
        document.querySelector(".download-btn-container").style.display = "block";

        statusDiv.className = "success";
        statusDiv.textContent = "✓ Image upscaled successfully!";
      };
      img.src = imageUrl;
    } catch (error) {
      statusDiv.className = "error";
      statusDiv.textContent = "✗ Error: " + error.message;

      // Hide upscaled preview on error
      upscaledWrapper.innerHTML = "";
      upscaledPreview.style.display = "none";
    } finally {
      submitBtn.disabled = false;
    }
  });
}

function showStatus(type, message) {
  const statusDiv = document.getElementById("status");
  statusDiv.style.display = "block";
  statusDiv.className = type;
  statusDiv.textContent = message;
}

function downloadImage() {
  if (uploadedImageData) {
    const url = URL.createObjectURL(uploadedImageData);
    const a = document.createElement("a");
    a.href = url;
    a.download = "upscaled_image.png";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}
