import { getPaletteTitleForType } from "./categories.js";
import { computeDropTopLeftWorld } from "./drop-math.js";

function findPaletteItemButton(target) {
  if (!(target instanceof Element)) {
    return null;
  }
  return target.closest(".palette-item");
}

function createGhost(text) {
  const ghost = document.createElement("div");
  ghost.className = "drag-ghost";
  ghost.textContent = text;
  document.body.appendChild(ghost);
  return ghost;
}

function positionGhost(ghost, clientX, clientY) {
  ghost.style.left = `${clientX + 12}px`;
  ghost.style.top = `${clientY + 12}px`;
}

export class PaletteDragDropHandler {
  constructor({ paletteRoot, canvas, canvasManager }) {
    this.paletteRoot = paletteRoot;
    this.canvas = canvas;
    this.canvasManager = canvasManager;

    this._dragging = null;

    this._onMouseDown = (e) => {
      const button = findPaletteItemButton(e.target);
      if (!button) {
        return;
      }

      const nodeType = button.dataset.nodeType;
      if (!nodeType) {
        return;
      }

      e.preventDefault();

      const title = button.textContent ?? nodeType;
      const ghost = createGhost(title);
      positionGhost(ghost, e.clientX, e.clientY);

      this._dragging = {
        nodeType,
        ghost,
      };
    };

    this._onMouseMove = (e) => {
      if (!this._dragging) {
        return;
      }
      positionGhost(this._dragging.ghost, e.clientX, e.clientY);
    };

    this._onMouseUp = (e) => {
      if (!this._dragging) {
        return;
      }

      const { nodeType, ghost } = this._dragging;
      this._dragging = null;
      ghost.remove();

      const rect = this.canvas.getBoundingClientRect();
      const inside =
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        e.clientY >= rect.top &&
        e.clientY <= rect.bottom;

      if (!inside) {
        return;
      }

      const screenPoint = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };

      const title = getPaletteTitleForType(nodeType) ?? nodeType;

      const nodeSize = { width: 180, height: 72 };
      const position = computeDropTopLeftWorld({
        screenPoint,
        viewport: this.canvasManager.viewport,
        nodeSize,
        gridSize: 10,
      });

      this.canvasManager.nodeManager.addFromPalette({
        type: nodeType,
        title,
        position,
      });
    };
  }

  attach() {
    this.paletteRoot.addEventListener("mousedown", this._onMouseDown);
    window.addEventListener("mousemove", this._onMouseMove);
    window.addEventListener("mouseup", this._onMouseUp);
  }

  detach() {
    this.paletteRoot.removeEventListener("mousedown", this._onMouseDown);
    window.removeEventListener("mousemove", this._onMouseMove);
    window.removeEventListener("mouseup", this._onMouseUp);
  }
}
