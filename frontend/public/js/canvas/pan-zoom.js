import { clampScale, panByScreenDelta, zoomAtScreenPoint } from "./viewport.js";

export class PanZoomController {
  constructor({ element, viewport }) {
    this.element = element;
    this.viewport = viewport;

    this._spaceDown = false;
    this._panning = false;
    this._last = { x: 0, y: 0 };

    this._onKeyDown = (e) => {
      if (e.code === "Space") {
        const target = e.target;
        const isEditable =
          target &&
          (target instanceof HTMLInputElement ||
            target instanceof HTMLTextAreaElement ||
            (target instanceof HTMLElement && target.isContentEditable));
        if (!isEditable) {
          e.preventDefault();
        }
        this._spaceDown = true;
      }
    };

    this._onKeyUp = (e) => {
      if (e.code === "Space") {
        const target = e.target;
        const isEditable =
          target &&
          (target instanceof HTMLInputElement ||
            target instanceof HTMLTextAreaElement ||
            (target instanceof HTMLElement && target.isContentEditable));
        if (!isEditable) {
          e.preventDefault();
        }
        this._spaceDown = false;
        this._panning = false;
      }
    };

    this._onMouseDown = (e) => {
      const isMiddle = e.button === 1;
      const isSpaceDrag = e.button === 0 && this._spaceDown;
      if (!isMiddle && !isSpaceDrag) {
        return;
      }

      e.preventDefault();
      if (isSpaceDrag) {
        // Space+drag should pan instead of interacting with nodes/wires.
        e.stopImmediatePropagation();
      }
      this._panning = true;
      this._last = { x: e.clientX, y: e.clientY };
    };

    this._onMouseMove = (e) => {
      if (!this._panning) {
        return;
      }

      const dx = e.clientX - this._last.x;
      const dy = e.clientY - this._last.y;
      this._last = { x: e.clientX, y: e.clientY };

      panByScreenDelta(this.viewport, { dx, dy });
    };

    this._onMouseUp = () => {
      this._panning = false;
    };

    this._onWheel = (e) => {
      // Only zoom when Ctrl+wheel occurs over the canvas.
      if (!e.ctrlKey) {
        return;
      }

      e.preventDefault();

      // Trackpads can send small deltas; use an exponential-ish curve.
      const direction = e.deltaY;
      const zoomFactor = Math.exp(-direction * 0.001);

      const nextScale = clampScale(this.viewport.scale * zoomFactor);
      zoomAtScreenPoint(this.viewport, { x: e.offsetX, y: e.offsetY }, nextScale);
    };
  }

  attach() {
    // Key events are global so space+drag works even if canvas isn't focused.
    window.addEventListener("keydown", this._onKeyDown);
    window.addEventListener("keyup", this._onKeyUp);

    // Pan/zoom events are on the canvas element.
    // Use capture so space+drag can intercept before selection/wire handlers.
    this.element.addEventListener("mousedown", this._onMouseDown, { capture: true });
    window.addEventListener("mousemove", this._onMouseMove);
    window.addEventListener("mouseup", this._onMouseUp);

    // Use { passive: false } so we can preventDefault and avoid page scroll.
    this.element.addEventListener("wheel", this._onWheel, { passive: false });
  }

  detach() {
    window.removeEventListener("keydown", this._onKeyDown);
    window.removeEventListener("keyup", this._onKeyUp);

    this.element.removeEventListener("mousedown", this._onMouseDown, { capture: true });
    window.removeEventListener("mousemove", this._onMouseMove);
    window.removeEventListener("mouseup", this._onMouseUp);

    this.element.removeEventListener("wheel", this._onWheel);
  }
}
