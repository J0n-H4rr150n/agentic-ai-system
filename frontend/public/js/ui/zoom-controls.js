export function createZoomControls({ rootEl, viewport, canvasManager }) {
    if (!rootEl) {
        throw new Error("createZoomControls: rootEl is required");
    }
    if (!viewport) {
        throw new Error("createZoomControls: viewport is required");
    }
    if (!canvasManager) {
        throw new Error("createZoomControls: canvasManager is required");
    }

    // Create zoom controls container
    const container = document.createElement("div");
    container.className = "zoom-controls";

    // Zoom in button
    const zoomInBtn = document.createElement("button");
    zoomInBtn.className = "zoom-control-button";
    zoomInBtn.textContent = "+";
    zoomInBtn.title = "Zoom in (Ctrl+=)";
    zoomInBtn.type = "button";

    // Zoom percentage display
    const zoomDisplay = document.createElement("div");
    zoomDisplay.className = "zoom-display";
    zoomDisplay.textContent = "100%";

    // Zoom out button
    const zoomOutBtn = document.createElement("button");
    zoomOutBtn.className = "zoom-control-button";
    zoomOutBtn.textContent = "−";
    zoomOutBtn.title = "Zoom out (Ctrl+-)";
    zoomOutBtn.type = "button";

    // Fit to screen button
    const fitBtn = document.createElement("button");
    fitBtn.className = "zoom-control-button zoom-control-button--wide";
    fitBtn.textContent = "Fit";
    fitBtn.title = "Fit to screen (Ctrl+0)";
    fitBtn.type = "button";

    // Clear canvas button
    const clearBtn = document.createElement("button");
    clearBtn.className = "zoom-control-button zoom-control-button--wide zoom-control-button--danger";
    clearBtn.textContent = "Clear";
    clearBtn.title = "Clear all nodes from canvas";
    clearBtn.type = "button";

    container.append(zoomInBtn, zoomDisplay, zoomOutBtn, fitBtn, clearBtn);
    rootEl.appendChild(container);

    // Update zoom display
    function updateDisplay() {
        const percentage = Math.round(viewport.scale * 100);
        zoomDisplay.textContent = `${percentage}%`;
    }

    // Get canvas center point
    function getCanvasCenter() {
        const canvas = canvasManager.canvas;
        return {
            x: canvas.width / 2,
            y: canvas.height / 2,
        };
    }

    // Import zoom functions (they'll be available from viewport.js)
    async function handleZoomIn() {
        const { zoomIn } = await import("../canvas/viewport.js");
        zoomIn(viewport, { centerScreen: getCanvasCenter() });
        updateDisplay();
    }

    async function handleZoomOut() {
        const { zoomOut } = await import("../canvas/viewport.js");
        zoomOut(viewport, { centerScreen: getCanvasCenter() });
        updateDisplay();
    }

    async function handleFit() {
        const { fitToScreen } = await import("../canvas/viewport.js");
        fitToScreen(viewport, {
            nodes: canvasManager.nodeManager.getNodes(),
            canvasWidth: canvasManager.canvas.width,
            canvasHeight: canvasManager.canvas.height,
        });
        updateDisplay();
    }

    // Event listeners
    zoomInBtn.addEventListener("click", handleZoomIn);
    zoomOutBtn.addEventListener("click", handleZoomOut);
    fitBtn.addEventListener("click", handleFit);
    clearBtn.addEventListener("click", () => {
        if (confirm("Clear all nodes from the canvas?\n\nThis cannot be undone.")) {
            const nodes = [...canvasManager.nodeManager.getNodes()];
            nodes.forEach(node => canvasManager.nodeManager.removeNode(node.id));
        }
    });

    // Keyboard shortcuts
    function handleKeyDown(e) {
        const isMod = e.ctrlKey || e.metaKey;
        if (!isMod) return;

        if (e.key === "=" || e.key === "+") {
            e.preventDefault();
            handleZoomIn();
        } else if (e.key === "-" || e.key === "_") {
            e.preventDefault();
            handleZoomOut();
        } else if (e.key === "0") {
            e.preventDefault();
            handleFit();
        } else if (e.key === "1") {
            e.preventDefault();
            viewport.scale = 1;
            updateDisplay();
        }
    }

    window.addEventListener("keydown", handleKeyDown);

    // Initial display
    updateDisplay();

    // Return API for manual updates
    return {
        updateDisplay,
        destroy() {
            window.removeEventListener("keydown", handleKeyDown);
            rootEl.removeChild(container);
        },
    };
}
