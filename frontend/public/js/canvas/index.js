import { createViewport } from "./viewport.js";
import { createRenderer } from "./renderer.js";
import { PanZoomController } from "./pan-zoom.js";
import { NodeManager } from "../nodes/index.js";
import { SelectionManager } from "../selection/index.js";
import { WireManager } from "../wires/index.js";
import { WireInteractionManager } from "../wires/interaction.js";
import { loadSampleSecurityWorkflow } from "../graph/sample-workflows.js";

export class CanvasManager {
  constructor({ canvas, host }) {
    if (!(canvas instanceof HTMLCanvasElement)) {
      throw new Error("canvas must be an HTMLCanvasElement");
    }
    this.canvas = canvas;
    this.host = host;

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      throw new Error("Could not get 2D context");
    }
    this.ctx = ctx;

    this.viewport = createViewport();
    this.nodeManager = new NodeManager();
    this.wireManager = new WireManager();

    loadSampleSecurityWorkflow({ nodeManager: this.nodeManager, wireManager: this.wireManager });

    this.wireInteraction = new WireInteractionManager({
      canvas,
      viewport: this.viewport,
      nodeManager: this.nodeManager,
      wireManager: this.wireManager,
    });

    this.selectionManager = new SelectionManager({
      canvas,
      viewport: this.viewport,
      nodeManager: this.nodeManager,
      gridSize: 10,
    });

    // Adapter so renderer can query selection without importing selection module.
    this.nodeManager.getSelectedNodeId = () => this.selectionManager.getSelectedNodeId();
    this.nodeManager.getHighlightedContainerId = () => this.selectionManager.getHighlightedContainerId();

    this.renderer = createRenderer({
      ctx,
      viewport: this.viewport,
      nodeManager: this.nodeManager,
      wireManager: this.wireManager,
      wireInteraction: this.wireInteraction,
    });
    this.panZoom = new PanZoomController({ element: canvas, viewport: this.viewport });

    this._resizeObserver = null;
    this._animationFrameId = null;
    this._running = false;
  }

  start() {
    if (this._running) {
      return;
    }
    this._running = true;

    this._resizeObserver = new ResizeObserver(() => {
      this.resizeToHost();
    });
    this._resizeObserver.observe(this.host);

    this.resizeToHost();
    this.panZoom.attach();
    this.wireInteraction.attach();
    this.selectionManager.attach();
    this._renderLoop();
  }

  stop() {
    this._running = false;

    this.panZoom.detach();
    this.wireInteraction.detach();
    this.selectionManager.detach();

    if (this._resizeObserver) {
      this._resizeObserver.disconnect();
      this._resizeObserver = null;
    }

    if (this._animationFrameId !== null) {
      cancelAnimationFrame(this._animationFrameId);
      this._animationFrameId = null;
    }
  }

  resizeToHost() {
    const rect = this.host.getBoundingClientRect();
    const nextWidth = Math.max(1, Math.floor(rect.width));
    const nextHeight = Math.max(1, Math.floor(rect.height));

    if (this.canvas.width !== nextWidth || this.canvas.height !== nextHeight) {
      this.canvas.width = nextWidth;
      this.canvas.height = nextHeight;
    }
  }

  _renderLoop() {
    if (!this._running) {
      return;
    }

    this.renderer.render({
      canvasWidth: this.canvas.width,
      canvasHeight: this.canvas.height,
    });

    this._animationFrameId = requestAnimationFrame(() => this._renderLoop());
  }
}
